import yaml
import os
from typing import List, Dict, Optional, Any
from crewai_tools import (
    SerperDevTool,
    ScrapeWebsiteTool,
    WebsiteSearchTool,
    # Add other tools as needed
)

# Map string names to actual classes
TOOL_CLASSES = {
    "SerperDevTool": SerperDevTool,
    "ScrapeWebsiteTool": ScrapeWebsiteTool,
    "WebsiteSearchTool": WebsiteSearchTool,
}

class ToolRegistry:
    def __init__(self, config_path: str = "config/tools.yaml"):
        self.config_path = config_path
        self._ensure_config_exists()

    def _ensure_config_exists(self):
        if not os.path.exists(self.config_path):
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                yaml.dump({"tools": []}, f)

    def _load_data(self) -> Dict:
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f) or {"tools": []}

    def _save_data(self, data: Dict):
        with open(self.config_path, 'w') as f:
            yaml.dump(data, f)

    def get_all_tools(self) -> List[Dict]:
        data = self._load_data()
        return data.get("tools", [])

    def create_tool(self, tool_data: Dict) -> Dict:
        data = self._load_data()
        if "tools" not in data:
            data["tools"] = []
        
        if any(t.get("name") == tool_data.get("name") for t in data["tools"]):
             raise ValueError(f"Tool with name '{tool_data.get('name')}' already exists.")

        # Validate Type
        if tool_data.get("type") not in TOOL_CLASSES:
             raise ValueError(f"Tool type '{tool_data.get('type')}' is not supported. Available: {list(TOOL_CLASSES.keys())}")

        data["tools"].append(tool_data)
        self._save_data(data)
        return tool_data

    def update_tool(self, name: str, tool_data: Dict) -> Optional[Dict]:
        data = self._load_data()
        tools = data.get("tools", [])
        
        for i, tool in enumerate(tools):
            if tool.get("name") == name:
                # Validation if type changes
                if "type" in tool_data and tool_data["type"] not in TOOL_CLASSES:
                    raise ValueError(f"Tool type '{tool_data.get('type')}' is not supported.")

                updated_tool = {**tool, **tool_data}
                updated_tool["name"] = name
                tools[i] = updated_tool
                data["tools"] = tools
                self._save_data(data)
                return updated_tool
        return None

    def delete_tool(self, name: str) -> bool:
        data = self._load_data()
        tools = data.get("tools", [])
        initial_len = len(tools)
        tools = [t for t in tools if t.get("name") != name]
        
        if len(tools) < initial_len:
            data["tools"] = tools
            self._save_data(data)
            return True
        return False
    
    def instantiate_tool(self, tool_config: Dict) -> Any:
        tool_type = tool_config.get("type")
        tool_class = TOOL_CLASSES.get(tool_type)
        if not tool_class:
            return None
        
        # Instantiate with arguments
        args = tool_config.get("arguments", {})
        # Safety check? for now pass **args
        try:
            return tool_class(**args)
        except Exception as e:
            print(f"Failed to instantiate tool {tool_config['name']}: {e}")
            return None
