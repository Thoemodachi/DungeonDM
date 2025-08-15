import chromadb
import os
import openai
from dotenv import load_dotenv


load_dotenv()
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
openai.api_key = OPENAI_API_KEY
EMBED_MODEL = "text-embedding-3-small"  # match DB

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../chroma_db"))
client = chromadb.PersistentClient(path=DB_PATH)

rules_col = client.get_or_create_collection("rules_and_refs")
campaign_col = client.get_or_create_collection("campaign")

def embed_query(text: str):
    response = openai.embeddings.create(
        model=EMBED_MODEL,
        input=text
    )
    return response.data[0].embedding

def retrieve_chunks(query: str, top_k=5):
    # Embed query using the same model as DB
    query_emb = embed_query(query)

    # Use embedding directly, no function attached to collection
    rules_results = rules_col.query(
        query_embeddings=[query_emb],
        n_results=top_k,
        include=["documents"]
    )

    campaign_results = campaign_col.query(
        query_embeddings=[query_emb],
        n_results=top_k,
        include=["documents"]
    )

    return rules_results['documents'][0] + campaign_results['documents'][0]


# -------------------------
# BUILD PROMPT FUNCTION
# -------------------------
def build_prompt(player_input, retrieved_chunks, character_id=None):
    prompt = "You are the DM. Follow the rules strictly.\n"
    for c in retrieved_chunks:
        prompt += f"{c}\n"
    prompt += f"Player input: {player_input}\n"
    if character_id:
        prompt += f"Player character: {character_id}\n"
    prompt += "Respond narratively and include any JSON deltas for game state."
    return prompt
