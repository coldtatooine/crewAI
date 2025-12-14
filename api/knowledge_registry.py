import os
from typing import List

class KnowledgeRegistry:
    def __init__(self, upload_dir: str = "knowledge"):
        self.upload_dir = upload_dir
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir, exist_ok=True)

    def save_file(self, filename: str, content: bytes) -> str:
        filepath = os.path.join(self.upload_dir, filename)
        with open(filepath, "wb") as f:
            f.write(content)
        return filepath

    def list_files(self) -> List[str]:
        return os.listdir(self.upload_dir)

    def delete_file(self, filename: str) -> bool:
        filepath = os.path.join(self.upload_dir, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False
    
    def get_file_path(self, filename: str) -> str:
        return os.path.abspath(os.path.join(self.upload_dir, filename))
