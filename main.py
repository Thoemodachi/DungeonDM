from fastapi import FastAPI
from pydantic import BaseModel
from backend.player_api import PlayerDrivenCampaign
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:3000",  # your frontend
    # "https://your-frontend.vercel.app"  # for production
]



app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],   # allow POST, GET, etc.
    allow_headers=["*"],
)
campaign = PlayerDrivenCampaign()

class PlayerInput(BaseModel):
    player_id: str
    input_text: str

@app.post("/play_turn")
def play_turn_endpoint(data: PlayerInput):
    result = campaign.play_turn(data.player_id, data.input_text)
    return result
