import uuid

from feed_data.save_file_chunk_config import ChunkStorageInformationManager
from settings import *
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import os
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
import fitz

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=OPENAI_API_KEY,
    model_name=OPEN_AI_EMBEDDING_MODEL_NAME
)

chroma_db_client = chromadb.HttpClient(host=CHROMA_DB_SERVER_IP, port=8000)
chroma_db_collection = chroma_db_client.get_or_create_collection(name=CHROMA_COLLECTION_NAME,
                                                                 embedding_function=openai_ef)

limit = 100
manager = ChunkStorageInformationManager()


def main():
    generate_data_store_one_by_one(TARGET_DIRECTORY_PATH)
    manager.print_counts()


def generate_data_store_one_by_one(paths: list):
    current_count = 0
    for data_path in paths:
        for root, dirs, files in os.walk(data_path):
            for file in files:
                file_name_without_extension, file_extension = os.path.splitext(file)
                # Remove the dot from the extension
                file_extension = file_extension[1:]
                if not manager.is_file_added(file_name_without_extension):
                    try:
                        print("\nProcessing file:", file_name_without_extension, "Extension:", file_extension)
                        file_path = os.path.join(root, file)
                        document = load_document(file_path)
                        chunks = split_text([document])  # Assuming these functions are defined elsewhere
                        save_chunks_to_chromadb(chunks)
                        manager.save_success(file_name_without_extension, file_extension, len(chunks))
                        current_count += 1
                    except Exception as e:
                        print(f"Error processing file: {file}. {e}")
                        manager.save_error(file_name_without_extension, file_extension, str(e))
                if current_count > limit:
                    return



def load_document(file_path):
    try:
        if file_path.lower().endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
        elif file_path.lower().endswith():
            content = ""
            with fitz.open(file_path) as file:
                for page in file:
                    content += page.get_text()
        else:
            raise Exception("Invalid file type.")
    except Exception as e:
        print(f"Error loading file: {file_path}. {e}")
        raise e
    finally:
        file.close()
    return Document(page_content=content, metadata={"path": file_path})


def split_text(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=200,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")
    return chunks


def save_chunks_to_chromadb(chunks):
    documents = [chunk.page_content for chunk in chunks]
    metadatas = [{**chunk.metadata, 'path': os.path.basename(chunk.metadata['path'])} for chunk in chunks]

    # generate unique ids every time
    ids = [uuid.uuid4().hex for index, _ in enumerate(chunks)]

    chroma_db_collection.add(documents=documents, metadatas=metadatas, ids=ids)
    print(f"Added {len(chunks)} chunks to the collection.")


if __name__ == "__main__":
    main()
