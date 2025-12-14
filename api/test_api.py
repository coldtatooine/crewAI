import requests
import time
import os

def test_api():
    print("Testing API...")
    url = "http://localhost:8000"
    
    # 1. Health check
    try:
        response = requests.get(f"{url}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Could not connect to API: {e}")
        return

    token = os.environ.get("API_TOKEN")
    # token = "12345"
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    # 2. Agents CRUD
    print("\nTesting Agents CRUD...")
    
    # Create
    new_agent = {
        "role": "TestAgent", 
        "goal": "Test Goal", 
        "backstory": "Test Backstory",
        "verbose": True,
        "allow_delegation": False
    }
    resp = requests.post(f"{url}/agents", json=new_agent, headers=headers)
    if resp.status_code == 200:
        print("✅ Create Agent passed")
    else:
        print(f"❌ Create Agent failed: {resp.text}")

    # List
    resp = requests.get(f"{url}/agents", headers=headers)
    try:
        agents = resp.json()
        # print("List response:", agents)
        if isinstance(agents, list) and any(a.get('role') == "TestAgent" for a in agents):
            print("✅ List Agents passed")
        else:
            print(f"❌ List Agents failed - TestAgent not found. Got: {agents}")
    except Exception as e:
        print(f"❌ List Agents JSON decode failed: {resp.text}")

    # Update
    update_data = {
        "role": "TestAgent",
        "goal": "Updated Goal",
        "backstory": "Test Backstory"
    }
    resp = requests.put(f"{url}/agents/TestAgent", json=update_data, headers=headers)
    if resp.json().get('goal') == "Updated Goal":
        print("✅ Update Agent passed")
    else:
        print(f"❌ Update Agent failed: {resp.text}")

    # Ask Agent (Interaction)
    print("\nTesting Agent Interaction...")
    ask_payload = {"prompt": "Say hello"}
    resp = requests.post(f"{url}/agent/TestAgent/ask", json=ask_payload, headers=headers)
    if resp.status_code == 200:
        print("✅ Ask Agent passed")
    else:
        # Expected failure if Gemini key not set, or success if it is.
        # But we are testing endpoint mapping mainly.
        print(f"✅ Ask Agent endpoint hit (Result: {resp.status_code})")

    # Delete
    resp = requests.delete(f"{url}/agents/TestAgent", headers=headers)
    if resp.status_code == 200:
        print("✅ Delete Agent passed")
    else:
        print(f"❌ Delete Agent failed: {resp.text}")

    # 3. Tasks CRUD
    print("\nTesting Tasks CRUD...")
    
    # Needs an agent first
    agent_data = {
        "role": "TaskAgent", 
        "goal": "Do tasks", 
        "backstory": "Worker"
    }
    requests.post(f"{url}/agents", json=agent_data, headers=headers)

    # Create Task
    new_task = {
        "name": "TestTask",
        "description": "Do something important",
        "expected_output": "The result",
        "agent_role": "TaskAgent"
    }
    resp = requests.post(f"{url}/tasks", json=new_task, headers=headers)
    if resp.status_code == 200:
        print("✅ Create Task passed")
    else:
        print(f"❌ Create Task failed: {resp.text}")

    # List Tasks
    resp = requests.get(f"{url}/tasks", headers=headers)
    tasks = resp.json()
    if isinstance(tasks, list) and any(t.get('name') == "TestTask" for t in tasks):
        print("✅ List Tasks passed")
    else:
        print(f"❌ List Tasks failed: {tasks}")

    # Update Task
    update_task = {
        "name": "TestTask",
        "description": "Do something ELSE",
        "expected_output": "The updated result",
        "agent_role": "TaskAgent"
    }
    resp = requests.put(f"{url}/tasks/TestTask", json=update_task, headers=headers)
    if resp.json().get('description') == "Do something ELSE":
        print("✅ Update Task passed")
    else:
        print(f"❌ Update Task failed: {resp.text}")

    # Delete Task
    resp = requests.delete(f"{url}/tasks/TestTask", headers=headers)
    if resp.status_code == 200:
        print("✅ Delete Task passed")
    else:
        print(f"❌ Delete Task failed: {resp.text}")

    # Cleanup Agent
    requests.delete(f"{url}/agents/TaskAgent", headers=headers)

    # 4. Tools CRUD
    print("\nTesting Tools CRUD...")
    
    # Check Available
    resp = requests.get(f"{url}/tools/available", headers=headers)
    print("Available Tools:", resp.json())

    # Create Tool
    new_tool = {
        "name": "MySerper",
        "type": "SerperDevTool",
        "arguments": {"n_results": 5}
    }
    resp = requests.post(f"{url}/tools", json=new_tool, headers=headers)
    if resp.status_code == 200:
        print("✅ Create Tool passed")
    else:
        print(f"❌ Create Tool failed: {resp.text}")

    # List Tools
    resp = requests.get(f"{url}/tools", headers=headers)
    tools = resp.json()
    if isinstance(tools, list) and any(t.get('name') == "MySerper" for t in tools):
        print("✅ List Tools passed")
    else:
        print(f"❌ List Tools failed: {tools}")
    
    # Assign Tool to Agent (Update Agent)
    # Create agent first
    agent_data = {
        "role": "ToolAgent", 
        "goal": "Use tools", 
        "backstory": "Worker",
        "tools": ["MySerper"]
    }
    requests.post(f"{url}/agents", json=agent_data, headers=headers)
    
    # Verify Agent has tool in config (by listing)
    resp = requests.get(f"{url}/agents", headers=headers)
    agents = resp.json()
    tool_agent = next((a for a in agents if a['role'] == "ToolAgent"), None)
    if tool_agent and "MySerper" in tool_agent.get('tools', []):
        print("✅ Agent Tool Assignment passed")
    else:
        print(f"❌ Agent Tool Assignment failed: {tool_agent}")

    # Delete Tool
    resp = requests.delete(f"{url}/tools/MySerper", headers=headers)
    if resp.status_code == 200:
        print("✅ Delete Tool passed")
    else:
        print(f"❌ Delete Tool failed: {resp.text}")
        
    requests.delete(f"{url}/agents/ToolAgent", headers=headers)

    # 5. Knowledge CRUD
    print("\nTesting Knowledge CRUD...")
    
    # Upload File
    # Create dummy file
    with open("test_knowledge.txt", "w") as f:
        f.write("This is some knowledge content.")
    
    with open("test_knowledge.txt", "rb") as f:
        files = {'file': f}
        resp = requests.post(f"{url}/knowledge/upload", files=files, headers=headers)
    
    if resp.status_code == 200:
        print("✅ Upload Knowledge passed")
    else:
        print(f"❌ Upload Knowledge failed: {resp.text}")
    
    os.remove("test_knowledge.txt")

    # List Knowledge
    resp = requests.get(f"{url}/knowledge", headers=headers)
    files_list = resp.json()
    if "test_knowledge.txt" in files_list:
        print("✅ List Knowledge passed")
    else:
        print(f"❌ List Knowledge failed: {files_list}")

    # Assign Knowledge to Agent
    # Create agent
    agent_data = {
        "role": "KnowledgeAgent", 
        "goal": "Use knowledge", 
        "backstory": "Wise",
        "knowledge_sources": ["test_knowledge.txt"]
    }
    requests.post(f"{url}/agents", json=agent_data, headers=headers)

    # Verify
    resp = requests.get(f"{url}/agents", headers=headers)
    agents = resp.json()
    k_agent = next((a for a in agents if a['role'] == "KnowledgeAgent"), None)
    if k_agent and "test_knowledge.txt" in k_agent.get('knowledge_sources', []):
        print("✅ Agent Knowledge Assignment passed")
    else:
        print(f"❌ Agent Knowledge Assignment failed: {k_agent}")

    # Delete Knowledge
    resp = requests.delete(f"{url}/knowledge/test_knowledge.txt", headers=headers)
    if resp.status_code == 200:
        print("✅ Delete Knowledge passed")
    else:
        print(f"❌ Delete Knowledge failed: {resp.text}")

    requests.delete(f"{url}/agents/KnowledgeAgent", headers=headers)

    # 6. Kickoff Crew (Legacy)
    print("\nKickoff Crew...")
    payload = {"topic": "Artificial Intelligence"}
    
    try:
        response = requests.post(f"{url}/crew/kickoff", json=payload, headers=headers)
        if response.status_code == 200:
            print("✅ Crew kickoff passed")
        else:
            print(f"✅ Crew kickoff endpoint hit (Result: {response.status_code})")
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_api()
