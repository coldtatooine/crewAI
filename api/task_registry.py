import yaml
import os
from typing import List, Dict, Optional

class TaskRegistry:
    def __init__(self, config_path: str = "config/tasks.yaml"):
        self.config_path = config_path
        self._ensure_config_exists()

    def _ensure_config_exists(self):
        if not os.path.exists(self.config_path):
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                yaml.dump({"tasks": []}, f)

    def _load_data(self) -> Dict:
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f) or {"tasks": []}

    def _save_data(self, data: Dict):
        with open(self.config_path, 'w') as f:
            yaml.dump(data, f)

    def get_all_tasks(self) -> List[Dict]:
        data = self._load_data()
        return data.get("tasks", [])

    def create_task(self, task_data: Dict) -> Dict:
        data = self._load_data()
        if "tasks" not in data:
            data["tasks"] = []
        
        # Simple ID generation or uniqueness check? 
        # For now, let's assume 'description' or a new 'name' field is unique-ish, 
        # or just append. Let's add a UUID if needed, but for simplicity, we just append.
        # Ideally, tasks should have a unique 'name' like agents.
        
        if any(t.get("name") == task_data.get("name") for t in data["tasks"]):
             raise ValueError(f"Task with name '{task_data.get('name')}' already exists.")

        data["tasks"].append(task_data)
        self._save_data(data)
        return task_data

    def update_task(self, name: str, task_data: Dict) -> Optional[Dict]:
        data = self._load_data()
        tasks = data.get("tasks", [])
        
        for i, task in enumerate(tasks):
            if task.get("name") == name:
                updated_task = {**task, **task_data}
                updated_task["name"] = name # Ensure name persistence
                tasks[i] = updated_task
                data["tasks"] = tasks
                self._save_data(data)
                return updated_task
        return None

    def delete_task(self, name: str) -> bool:
        data = self._load_data()
        tasks = data.get("tasks", [])
        initial_len = len(tasks)
        tasks = [t for t in tasks if t.get("name") != name]
        
        if len(tasks) < initial_len:
            data["tasks"] = tasks
            self._save_data(data)
            return True
        return False
