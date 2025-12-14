# CrewAI Studio API Documentation

Base URL: `https://crew.agritalk.com.br` (or `http://localhost:8000` locally)

## Authentication
This API uses Bearer Token authentication.
You must provide the `API_TOKEN` in the `Authorization` header.

**Header Format:**
`Authorization: Bearer YOUR_SECRET_TOKEN`

## Endpoints

### 1. Health Check
Checks if the API service is running and healthy. This endpoint is public (no auth required).

- **URL**: `/health`
- **Method**: `GET`
- **Response**:
    ```json
    { "status": "healthy" }
    ```

---

### 2. Agents Management

#### List Agents
- **URL**: `/agents`
- **Method**: `GET`
- **Response**: List of AgentConfig objects.

#### Create Agent
- **URL**: `/agents`
- **Method**: `POST`
- **Body**:
    ```json
    {
        "role": "Researcher",
        "goal": "Research topics",
        "backstory": "Expert researcher",
        "verbose": true,
        "allow_delegation": false,
        "tools": ["ToolName"],
        "knowledge_sources": ["file.txt"]
    }
    ```

#### Update Agent
- **URL**: `/agents/{role}`
- **Method**: `PUT`
- **Body**: Same as Create Agent.

#### Delete Agent
- **URL**: `/agents/{role}`
- **Method**: `DELETE`

#### Ask Agent (Interaction)
Execute a prompt with a specific agent.
- **URL**: `/agent/{role}/ask`
- **Method**: `POST`
- **Body**: `{ "prompt": "What is AI?" }`

---

### 3. Tasks Management

#### List Tasks
- **URL**: `/tasks`
- **Method**: `GET`

#### Create Task
- **URL**: `/tasks`
- **Method**: `POST`
- **Body**:
    ```json
    {
        "name": "TaskName",
        "description": "Task description",
        "expected_output": "Output expectation",
        "agent_role": "Researcher"
    }
    ```

#### Update Task
- **URL**: `/tasks/{name}`
- **Method**: `PUT`

#### Delete Task
- **URL**: `/tasks/{name}`
- **Method**: `DELETE`

---

### 4. Tools Management

#### List Tools
- **URL**: `/tools`
- **Method**: `GET`

#### List Available Tool Types
- **URL**: `/tools/available`
- **Method**: `GET`

#### Create Tool
- **URL**: `/tools`
- **Method**: `POST`
- **Body**:
    ```json
    {
        "name": "MySearch",
        "type": "SerperDevTool",
        "arguments": { "n_results": 5 }
    }
    ```

#### Delete Tool
- **URL**: `/tools/{name}`
- **Method**: `DELETE`

---

### 5. Knowledge Management

#### Upload Knowledge File
- **URL**: `/knowledge/upload`
- **Method**: `POST`
- **Body**: Multipart file upload (`file` field).

#### List Knowledge Files
- **URL**: `/knowledge`
- **Method**: `GET`

#### Delete Knowledge File
- **URL**: `/knowledge/{filename}`
- **Method**: `DELETE`

---

### 6. Crew Execution (Legacy)
Triggers the CrewAI agent(s) to start processing a specific topic using a default logic.

- **URL**: `/crew/kickoff`
- **Method**: `POST`
- **Body**: `{ "topic": "Your topic" }`
