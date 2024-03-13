import os

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
OPEN_AI_EMBEDDING_MODEL_NAME = "text-embedding-3-large"
CHROMA_DB_SERVER_IP = "65.1.92.45"
#CHROMA_DB_SERVER_IP = "localhost"

CHROMA_DB_SERVER_HOST = 8000

DATA_DIRECTORY_PATH = ["/Users/panshulgarg/Downloads/toc_notifications_2023_1991/notifications_not_in_toc/",
                       "/Users/panshulgarg/Downloads/toc_notifications_2023_1991/notification_1991_2023/"]

target_dir_accepted_txt = "/Users/panshulgarg/dev/ai_projects/sarvam_test/rbi_notifications_rag/feed_data/data_path/compatible_files/txt_files"
target_dir_accepted_pdf = "/Users/panshulgarg/dev/ai_projects/sarvam_test/rbi_notifications_rag/feed_data/data_path/compatible_files/pdf_files"
TARGET_DIRECTORY_PATH = [target_dir_accepted_txt, target_dir_accepted_txt]
FILE_EXTENSIONS = [".pdf", ".html", ".htm"]

CHROMA_COLLECTION_NAME = "rbi_notifications_chunks"
