import yaml
import os
from typing import List, Dict, Optional

class AgentRegistry:
    def __init__(self, config_path: str = "config/agents.yaml"):
        self.config_path = config_path
        self._ensure_config_exists()

    def _ensure_config_exists(self):
        if not os.path.exists(self.config_path):
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                yaml.dump({"agents": []}, f)

    def _load_data(self) -> Dict:
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f) or {"agents": []}

    def _save_data(self, data: Dict):
        with open(self.config_path, 'w') as f:
            yaml.dump(data, f)

    def get_all_agents(self) -> List[Dict]:
        data = self._load_data()
        return data.get("agents", [])

    def get_agent_by_role(self, role: str) -> Optional[Dict]:
        agents = self.get_all_agents()
        for agent in agents:
            if agent.get("role") == role:
                return agent
        return None

    def create_agent(self, agent_data: Dict) -> Dict:
        data = self._load_data()
        if "agents" not in data:
            data["agents"] = []
        
        # Check if agent exists
        if any(a.get("role") == agent_data.get("role") for a in data["agents"]):
            raise ValueError(f"Agent with role '{agent_data.get('role')}' already exists.")

        data["agents"].append(agent_data)
        self._save_data(data)
        return agent_data

    def update_agent(self, role: str, agent_data: Dict) -> Optional[Dict]:
        data = self._load_data()
        agents = data.get("agents", [])
        
        for i, agent in enumerate(agents):
            if agent.get("role") == role:
                # Update fields (allow partial update logic if desired, or full replace)
                # Here we'll do a merge/replace but keep the role if not provided in agent_data (though it should handle rename?)
                # For simplicity, assume role is the ID and immutable for now, or handle rename carefully.
                # Let's assume we are just updating content.
                updated_agent = {**agent, **agent_data}
                # Ensure role matches key if we don't want to allow renaming via this method easily
                updated_agent["role"] = role 
                
                agents[i] = updated_agent
                data["agents"] = agents
                self._save_data(data)
                return updated_agent
        return None

    def delete_agent(self, role: str) -> bool:
        data = self._load_data()
        agents = data.get("agents", [])
        initial_len = len(agents)
        agents = [a for a in agents if a.get("role") != role]
        
        if len(agents) < initial_len:
            data["agents"] = agents
            self._save_data(data)
            return True
        return False
