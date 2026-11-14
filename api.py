import os
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from green_life_ai import recommend_trees_for_location, diagnose_plant_chat

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class LocationRequest(BaseModel):
    city: str

class ChatRequest(BaseModel):
    tree_name: str
    location_name: str
    chat_history: list 
    @app.get("/favicon.ico", include_in_schema=False) 
    def favicon():
        return Response(status_code=204) 

@app.get("/")
def serve_app():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(base_dir, "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return Response(content=html_content, media_type="text/html")

@app.post("/recommend")
def get_trees(req: LocationRequest):
    return recommend_trees_for_location(req.city)

@app.post("/diagnose")
def get_diagnosis(req: ChatRequest):
    reply = diagnose_plant_chat(req.tree_name, req.location_name, req.chat_history)
    return {"reply": reply}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000) 
