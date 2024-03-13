json_data_format = {
    "compatible_files_added": {},
    "compatible_files_error": {},
}

import json
import os


class ChunkStorageInformationManager:
    def __init__(self):
        self.json_file_path = "./data_report.json"
        self.data = self.load_json()

    def load_json(self):
        if os.path.exists(self.json_file_path):
            with open(self.json_file_path, 'r') as file:
                return json.load(file)
        else:
            return {"compatible_files_added": {}, "compatible_files_error": {}}

    def save_json(self):
        try:
            with open(self.json_file_path, 'w') as file:
                json.dump(self.data, file, indent=4)
        finally:
            file.close()

    def update_file(self, file_name, extension, chunk=None, error=None):
        if chunk is not None:
            self.data["compatible_files_added"][file_name] = {
                "extension": extension,
                "chunks": chunk,
            }
        elif error is not None:
            self.data["compatible_files_error"][file_name] = {
                "extension": extension,
                "error": error,
            }
        self.save_json()

    def save_success(self, file_name, extension, chunk):
        if self.is_file_errored(file_name):
            self.data["compatible_files_error"].pop(file_name)
        self.update_file(file_name, extension, chunk=chunk)



    def save_error(self, file_name, extension, error):
        self.update_file(file_name, extension, error=error)

    def get_counts(self):
        added_count = len(self.data["compatible_files_added"])
        error_count = len(self.data["compatible_files_error"])
        return added_count, error_count

    def print_counts(self):
        added_count, error_count = self.get_counts()
        print(f"Files successfully processed: {added_count}, Files with errors: {error_count}")

    def is_file_added(self, file_name):
        return file_name in self.data["compatible_files_added"].keys()

    def is_file_errored(self, file_name):
        return file_name in self.data["compatible_files_error"].keys()


# Example usage
manager = ChunkStorageInformationManager()

# print(manager.update_file('example', '.txt', chunk='5'))
# print(manager.update_file('example2', '.html', error='File not found'))
#
# added_count, error_count = manager.get_counts()
# print(f"Files successfully processed: {added_count}, Files with errors: {error_count}")
