import re

from bs4 import BeautifulSoup

from settings import DATA_DIRECTORY_PATH

target_dir_accepted_txt = "/Users/panshulgarg/dev/ai_projects/sarvam_test/rbi_notifications_rag/feed_data/data_path/compatible_files/txt_files"
target_dir_accepted_pdf = "/Users/panshulgarg/dev/ai_projects/sarvam_test/rbi_notifications_rag/feed_data/data_path/compatible_files/pdf_files"
not_accepted_files_dir = "/Users/panshulgarg/dev/ai_projects/sarvam_test/rbi_notifications_rag/feed_data/data_path/non_compatible_files/"

import os
import shutil


def convert_html_to_txt(html_file, new_target_path):
    with open(html_file) as file:
        soup = BeautifulSoup(file, 'html.parser')

        text = soup.get_text(separator=' ', strip=True)
        text = re.sub(r'[^\w\s]', '', text).lower()

        with open(new_target_path, 'w') as txt_file:
            txt_file.write(text)


def move_files():
    #text_dir = ["/Users/panshulgarg/dev/ai_projects/sarvam_test/rbi_notifications_rag/test_directory/"]
    for source_dir in DATA_DIRECTORY_PATH:
        for filename in os.listdir(source_dir):
            file_path = os.path.join(source_dir, filename)
            if os.path.isfile(file_path):
                extension = os.path.splitext(filename)[1].lower()

                if extension == '.html' or extension == '.htm':
                    new_filename = os.path.splitext(filename)[0] + '.txt'
                    new_target_path = os.path.join(target_dir_accepted_txt, new_filename)
                    convert_html_to_txt(file_path, new_target_path)
                    print(f"{filename}: File moved to txt_files directory")
                elif extension == '.pdf':
                    shutil.copy(file_path, os.path.join(target_dir_accepted_pdf, filename))
                    print(f"{filename}: File moved to pdf directory")
                else:
                    shutil.copy(file_path, os.path.join(not_accepted_files_dir, filename))
                    print(f"{filename}: File Incompatible")


if __name__ == '__main__':
    move_files()
