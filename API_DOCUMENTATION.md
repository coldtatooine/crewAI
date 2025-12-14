# CrewAI API Documentation

Base URL: `https://crew.agritalk.com.br`

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
    {
      "status": "healthy"
    }
    ```

### 2. Kickoff Crew
Triggers the CrewAI agent(s) to start processing a specific topic.

- **URL**: `/crew/kickoff`
- **Method**: `POST`
- **Headers**:
    - `Content-Type: application/json`
- **Request Body**:
    ```json
    {
      "topic": "Your research topic here"
    }
    ```
- **Success Response (200 OK)**:
    ```json
    {
      "result": "The final output string from the crew.",
      "status": "success"
    }
    ```
- **Error Response (500 Internal Server Error)**:
    ```json
    {
      "detail": "Error description"
    }
    ```

## Example Usage

### CURL
```bash
curl -X POST https://crew.agritalk.com.br/crew/kickoff \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_SECRET_TOKEN" \
  -d '{"topic": "Future of Agriculture"}'
```

### Python
```python
import requests

url = "https://crew.agritalk.com.br/crew/kickoff"
headers = {"Authorization": "Bearer YOUR_SECRET_TOKEN"}
payload = {"topic": "Future of Agriculture"}

response = requests.post(url, json=payload, headers=headers)
print(response.json())
```
