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


def retrieve_chunks(query: str, top_k=5, return_scores=False, collection=None):
    """Retrieve top_k chunks from a specific collection (rules or campaign)."""
    query_emb = embed_query(query)

    if collection is None:
        # Default: search both
        rules_results = rules_col.query(
            query_embeddings=[query_emb],
            n_results=top_k,
            include=["documents", "distances"]
        )
        campaign_results = campaign_col.query(
            query_embeddings=[query_emb],
            n_results=top_k,
            include=["documents", "distances"]
        )
        combined_docs = rules_results['documents'][0] + campaign_results['documents'][0]
        combined_scores = rules_results['distances'][0] + campaign_results['distances'][0]
    else:
        results = collection.query(
            query_embeddings=[query_emb],
            n_results=top_k,
            include=["documents", "distances"]
        )
        combined_docs = results['documents'][0]
        combined_scores = results['distances'][0]

    if return_scores:
        return combined_docs, combined_scores
    return combined_docs



def build_prompt(player_input, retrieved_chunks, character_id=None):
    """Build the DM prompt using retrieved chunks."""
    prompt = "You are the DM. Follow the rules strictly.\n"
    for c in retrieved_chunks:
        prompt += f"{c}\n"
    prompt += f"Player input: {player_input}\n"
    if character_id:
        prompt += f"Player character: {character_id}\n"
    prompt += "Respond narratively and include any JSON deltas for game state."
    return prompt
