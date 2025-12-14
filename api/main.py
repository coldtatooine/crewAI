from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from api.crew import ApiCrew
import os

app = FastAPI(title="CrewAI API", description="API to run CrewAI crews", version="1.0.0")
security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    expected_token = os.environ.get("API_TOKEN")
    if not expected_token:
        # If API_TOKEN is not set, allow all (or fail secure, depending on pref. Let's fail secure)
        raise HTTPException(status_code=500, detail="API_TOKEN configuration missing")
    if token != expected_token:
        raise HTTPException(status_code=403, detail="Invalid authentication credentials")
    return token

class KickoffRequest(BaseModel):
    topic: str

@app.get("/health")
def health_check():
    return {"status": "healthy"}

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
