from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from api.crew import ApiCrew
import os

app = FastAPI(title="CrewAI API", description="API to run CrewAI crews", version="1.0.0")

class KickoffRequest(BaseModel):
    topic: str

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/crew/kickoff")
def kickoff_crew(request: KickoffRequest):
    """
    Kicks off the crew with the given topic.
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
