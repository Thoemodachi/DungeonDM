import chromadb
from chromadb.utils import embedding_functions
import openai, os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.environ["OPENAI_API_KEY"]
MODEL = "text-embedding-3-small"

def embed_text(text):
    return openai.embeddings.create(model=MODEL, input=text).data[0].embedding  # returns list of floats

# Initialize ChromaDB client
client = chromadb.PersistentClient(path="./chroma_db")

# Attempt to get the existing collection; raise error if not found
col_name = "campaign"
try:
    collection = client.get_collection(col_name)
except Exception as e:
    raise RuntimeError(f"ChromaDB collection '{col_name}' does not exist. Please create it before running this script.") from e

# Define all campaign chunks
campaign_chunks = [
    # Phase 1
    {
        "phase": 1, "chunk_id": 1, "text": "The adventurers arrive in Nightstone. The village is in ruins; structures are partially collapsed, and goblins roam the streets.",
        "npc_focus": ["Morak"], "location": "Nightstone", "trigger_keywords": ["goblins defeated"]
    },
    {
        "phase": 1, "chunk_id": 2, "text": "Villagers are imprisoned in caves. Goblins patrol the Nightstone Inn, farms, and towers.",
        "npc_focus": ["Morak", "Kella Darkhope"], "location": "Nightstone", "trigger_keywords": ["Nightstone cleared"]
    },
    {
        "phase": 1, "chunk_id": 3, "text": "Characters explore the Nightstone Inn, Temple, and Lionshield Coster. They encounter minor goblins and traps.",
        "npc_focus": ["Morak"], "location": "Nightstone", "trigger_keywords": ["Nightstone cleared"]
    },

    # Phase 2
    {
        "phase": 2, "chunk_id": 1, "text": "The Seven Snakes arrive, disguised as bounty hunters. Their leader, Xolkin, eyes Kella Darkhope and plans to secure the village.",
        "npc_focus": ["Xolkin", "Kella"], "location": "Nightstone", "trigger_keywords": ["Zhentarim confronted"]
    },
    {
        "phase": 2, "chunk_id": 2, "text": "Orcs of the Ear Seekers attack Nightstone. The party can defend or negotiate.",
        "npc_focus": ["War Chief Gurrash", "Norgra"], "location": "Nightstone", "trigger_keywords": ["orcs defeated"]
    },
    {
        "phase": 2, "chunk_id": 3, "text": "Wood elves led by Rond Arrowhome may arrive to assist. Their aid is temporary.",
        "npc_focus": ["Rond Arrowhome", "elves"], "location": "Nightstone", "trigger_keywords": ["siege resolved"]
    },

    # Phase 3
    {
        "phase": 3, "chunk_id": 1, "text": "Characters enter the Dripping Caves. Villagers are imprisoned; goblins patrol.",
        "npc_focus": ["Morak", "villagers"], "location": "Dripping Caves", "trigger_keywords": ["prisoners freed"]
    },
    {
        "phase": 3, "chunk_id": 2, "text": "Encounter goblin boss Hark and his giant rats; negotiation or combat is possible.",
        "npc_focus": ["Hark", "Snigbat"], "location": "Dripping Caves", "trigger_keywords": ["boss defeated"]
    },
    {
        "phase": 3, "chunk_id": 3, "text": "Deal with threats inside the caves: ogres Nob & Thog, black pudding, bats, poisonous mushrooms.",
        "npc_focus": ["Nob", "Thog", "blob"], "location": "Dripping Caves", "trigger_keywords": ["caves cleared"]
    },

    # Phase 4
    {
        "phase": 4, "chunk_id": 1, "text": "Morak offers a choice of three quests: Bryn Shander, Goldenfields, Triboar.",
        "npc_focus": ["Morak"], "location": "Nightstone", "trigger_keywords": ["quest chosen"]
    },
    {
        "phase": 4, "chunk_id": 2, "text": "Zephyros’ tower descends; cloud stairs form. Zephyros introduces the characters to giant-scale furnishings.",
        "npc_focus": ["Zephyros"], "location": "Tower of Zephyros", "trigger_keywords": ["tower boarded"]
    },
    {
        "phase": 4, "chunk_id": 3, "text": "Characters encounter Unfriendly Skies: cultists Amarath & N’von arrive, chaos ensues.",
        "npc_focus": ["Amarath", "N’von", "cultists"], "location": "Tower of Zephyros", "trigger_keywords": ["cultists handled"]
    },
    {
        "phase": 4, "chunk_id": 4, "text": "Optional encounter: Operation 'Orb Strike' with Clarion the silver dragon and dwarves.",
        "npc_focus": ["Clarion", "dwarves"], "location": "Tower of Zephyros", "trigger_keywords": ["orb secured"]
    },

    # Phase 5
    {
        "phase": 5, "chunk_id": 1, "text": "Characters complete their chosen quest; impact on NPCs and locations is evaluated.",
        "npc_focus": ["Quest NPCs", "Morak"], "location": "Quest destinations", "trigger_keywords": ["quest completed"]
    },
    {
        "phase": 5, "chunk_id": 2, "text": "Zephyros rewards the adventurers, offers guidance for the next journey.",
        "npc_focus": ["Zephyros"], "location": "Tower of Zephyros", "trigger_keywords": ["rewards collected"]
    },
    {
        "phase": 5, "chunk_id": 3, "text": "Open hooks for further adventures based on previous choices; world state updated.",
        "npc_focus": ["All relevant NPCs"], "location": "Various", "trigger_keywords": ["phase 5 concluded"]
    },
]

for chunk in campaign_chunks:
    embedding = embed_text(chunk["text"])  # list of floats
    collection.add(
        documents=[chunk["text"]],
        metadatas=[{
            "phase": chunk["phase"],
            "chunk_id": chunk["chunk_id"],
            "npc_focus": ", ".join(chunk["npc_focus"]),
            "location": chunk["location"],
            "trigger_keywords": ", ".join(chunk["trigger_keywords"])
        }],
        embeddings=[embedding],  # ✅ plain list of floats
        ids=[f"phase{chunk['phase']}_chunk{chunk['chunk_id']}"]
    )


print("Campaign chunks successfully preloaded into ChromaDB.")