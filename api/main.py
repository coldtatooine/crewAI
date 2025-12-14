from fastapi import FastAPI, HTTPException, Security, Depends, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional, Dict
from api.crew import ApiCrew
from api.agent_registry import AgentRegistry
from api.task_registry import TaskRegistry
from api.tool_registry import ToolRegistry, TOOL_CLASSES
from api.knowledge_registry import KnowledgeRegistry
import os

app = FastAPI(title="CrewAI API", description="API to run CrewAI crews", version="1.0.0")
security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    expected_token = os.environ.get("API_TOKEN", "").strip()
    if not expected_token:
        # If API_TOKEN is not set, allow all (or fail secure, depending on pref. Let's fail secure)
        raise HTTPException(status_code=500, detail="API_TOKEN configuration missing")
    if token != expected_token:
        # Debugging purposes
        print(f"Auth Mismatch: Received '{token}' vs Expected '{expected_token}'")
        raise HTTPException(status_code=403, detail=f"Invalid authentication credentials. Got: '{token}', Expected: '{expected_token}'")
    return token

class KickoffRequest(BaseModel):
    topic: str

class AgentConfig(BaseModel):
    role: str
    goal: str
    backstory: str
    verbose: bool = True
    allow_delegation: bool = False
    verbose: bool = True
    allow_delegation: bool = False
    tools: List[str] = [] # List of tool names
    knowledge_sources: List[str] = [] # List of filenames

class ToolConfig(BaseModel):
    name: str # Acts as ID
    type: str
    arguments: Dict = {}

class AgentTaskRequest(BaseModel):
    prompt: str

class TaskConfig(BaseModel):
    name: str # Acts as ID
    description: str
    expected_output: str
    agent_role: Optional[str] = None # Link to an agent by role

registry = AgentRegistry()
task_registry = TaskRegistry()
tool_registry = ToolRegistry()
knowledge_registry = KnowledgeRegistry()

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/agents", response_model=List[AgentConfig])
def list_agents(token: str = Depends(verify_token)):
    return registry.get_all_agents()

@app.post("/agents", response_model=AgentConfig)
def create_agent(agent: AgentConfig, token: str = Depends(verify_token)):
    try:
        return registry.create_agent(agent.dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/agents/{role}", response_model=AgentConfig)
def update_agent(role: str, agent: AgentConfig, token: str = Depends(verify_token)):
    updated = registry.update_agent(role, agent.dict())
    if not updated:
        raise HTTPException(status_code=404, detail="Agent not found")
    return updated

@app.delete("/agents/{role}")
def delete_agent(role: str, token: str = Depends(verify_token)):
    deleted = registry.delete_agent(role)
    if not deleted:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"status": "success", "message": f"Agent {role} deleted"}

# --- Tasks Endpoints ---

@app.get("/tasks", response_model=List[TaskConfig])
def list_tasks(token: str = Depends(verify_token)):
    return task_registry.get_all_tasks()

@app.post("/tasks", response_model=TaskConfig)
def create_task(task: TaskConfig, token: str = Depends(verify_token)):
    try:
        return task_registry.create_task(task.dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/tasks/{name}", response_model=TaskConfig)
def update_task(name: str, task: TaskConfig, token: str = Depends(verify_token)):
    updated = task_registry.update_task(name, task.dict())
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated

@app.delete("/tasks/{name}")
def delete_task(name: str, token: str = Depends(verify_token)):
    deleted = task_registry.delete_task(name)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"status": "success", "message": f"Task {name} deleted"}

@app.delete("/tasks/{name}")
def delete_task(name: str, token: str = Depends(verify_token)):
    deleted = task_registry.delete_task(name)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"status": "success", "message": f"Task {name} deleted"}

# --- Tools Endpoints ---

@app.get("/tools", response_model=List[ToolConfig])
def list_tools(token: str = Depends(verify_token)):
    return tool_registry.get_all_tools()

@app.get("/tools/available")
def list_available_tool_types(token: str = Depends(verify_token)):
    return list(TOOL_CLASSES.keys())

@app.post("/tools", response_model=ToolConfig)
def create_tool(tool: ToolConfig, token: str = Depends(verify_token)):
    try:
        return tool_registry.create_tool(tool.dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/tools/{name}", response_model=ToolConfig)
def update_tool(name: str, tool: ToolConfig, token: str = Depends(verify_token)):
    updated = tool_registry.update_tool(name, tool.dict())
    if not updated:
        raise HTTPException(status_code=404, detail="Tool not found")
    return updated

@app.delete("/tools/{name}")
def delete_tool(name: str, token: str = Depends(verify_token)):
    deleted = tool_registry.delete_tool(name)
    if not deleted:
        raise HTTPException(status_code=404, detail="Tool not found")
    return {"status": "success", "message": f"Tool {name} deleted"}

    return {"status": "success", "message": f"Tool {name} deleted"}

# --- Knowledge Endpoints ---

@app.post("/knowledge/upload")
async def upload_knowledge(file: UploadFile = File(...), token: str = Depends(verify_token)):
    try:
        content = await file.read()
        knowledge_registry.save_file(file.filename, content)
        return {"filename": file.filename, "status": "uploaded"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/knowledge")
def list_knowledge(token: str = Depends(verify_token)):
    return knowledge_registry.list_files()

@app.delete("/knowledge/{filename}")
def delete_knowledge(filename: str, token: str = Depends(verify_token)):
    deleted = knowledge_registry.delete_file(filename)
    if not deleted:
        raise HTTPException(status_code=404, detail="File not found")
    return {"status": "success", "message": f"File {filename} deleted"}

@app.post("/agent/{role}/ask")
def ask_agent(role: str, request: AgentTaskRequest, token: str = Depends(verify_token)):
    """
    Asks a specific agent a question/task.
    """
    try:
        # We will use ApiCrew to run this, specifically targeting one agent
        # For now, let's assume ApiCrew can handle this, or we construct it here.
        # But to keep logic encapsulated, let's look at ApiCrew refactor.
        # For now, we'll placeholder this or implement it via ApiCrew.
        result = ApiCrew().run_single_agent_task(role, request.prompt)
        return {"result": str(result), "status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/crew/kickoff")
def kickoff_crew(request: KickoffRequest, token: str = Depends(verify_token)):
    """
    Kicks off the crew with the given topic. Requires Bearer Token.
    """
    try:
        inputs = {"topic": request.topic}
        crew_instance = ApiCrew().crew()
        result = crew_instance.kickoff(inputs=inputs)
        return {"result": str(result), "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
