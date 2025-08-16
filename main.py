from fastapi import FastAPI
from pydantic import BaseModel
from backend.player_api import PlayerDrivenCampaign
from fastapi.middleware.cors import CORSMiddleware

origins = ["http://localhost:3000"]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

campaign = PlayerDrivenCampaign()

class NameRequest(BaseModel):
    name: str

class PlayerInput(BaseModel):
    player_id: str
    input_text: str

@app.post("/start_game")
def start_game(request: NameRequest):
    """Register player and return greeting, no story yet"""
    player_id = request.name.lower().replace(" ", "_")

    return {
        "player_id": player_id,
        "narration": f"Hello {request.name}, your name has been registered. Type something to start your adventure!",
        "scene_audio": "exploration_travel"  # optional default background
    }

@app.post("/play_turn")
def play_turn_endpoint(data: PlayerInput):
    """Normal gameplay after story begins"""
    result = campaign.play_turn(data.player_id, data.input_text)
    return {
        "player_id": data.player_id,
        "narration": result["narration"],
        "scene_audio": result["scene_audio"],
    }
