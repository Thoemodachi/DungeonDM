import os
import chromadb
from .memory import add_event, get_recent_events
from .llm_client import generate_response
import openai

MAX_PROMPT_CHARS = 4000
SIMILARITY_THRESHOLD = 0.75  # cosine similarity threshold for enforcing rules

def truncate_text(text, max_chars=MAX_PROMPT_CHARS):
    return text[-max_chars:] if len(text) > max_chars else text

class PlayerDrivenCampaign:
    """
    Player-driven campaign with conditional 5e rules enforcement.
    LLM narrates freely unless player input matches rules closely.
    """

    def __init__(self, db_path="./chroma_db"):
        abs_path = os.path.abspath(db_path)
        self.client = chromadb.PersistentClient(path=abs_path)
        self.rules_col = self.client.get_or_create_collection("rules_and_refs")
        self.campaign_col = self.client.get_or_create_collection("campaign")
        self.embed_model = "text-embedding-3-small"

    def embed_text(self, text):
        return openai.embeddings.create(model=self.embed_model, input=text).data[0].embedding

    def retrieve_chunks_with_similarity(self, query, top_k=5, collection=None):
        """Retrieve chunks with similarity scores (0-1)."""
        if collection is None:
            return [], []

        query_emb = self.embed_text(query)
        results = collection.query(
            query_embeddings=[query_emb],
            n_results=top_k,
            include=["documents", "distances"]
        )

        docs = results["documents"][0] if results["documents"] else []
        # Chroma returns distances, convert to similarity (cosine) if distance=1-similarity
        sims = [1 - d for d in results["distances"][0]] if results.get("distances") else [0] * len(docs)
        return docs, sims

    def enforce_rules(self, player_input):
        """Check rules only if similarity exceeds threshold."""
        docs, sims = self.retrieve_chunks_with_similarity(player_input, top_k=5, collection=self.rules_col)
        if not sims or max(sims) < SIMILARITY_THRESHOLD:
            return ""  # LLM can improvise freely
        return "According to D&D 5e rules, you can only:\n" + "\n".join(docs)

    def get_inspiration(self, player_input):
        """Always retrieve campaign inspiration (optional)."""
        docs, _ = self.retrieve_chunks_with_similarity(player_input, top_k=3, collection=self.campaign_col)
        if docs:
            return "Inspiration from the campaign:\n" + "\n".join(docs)
        return ""

    def play_turn(self, player_id, player_input):
        """Generate the next story segment based on player's input."""
        recent_mem = get_recent_events(player_id, limit=20)
        mem_text = "\n".join([f"{e['type']}: {e['description']}" for e in recent_mem])

        rule_guidance = self.enforce_rules(player_input)
        inspiration_text = self.get_inspiration(player_input)

        prompt_parts = [
            "You are the Dungeon Master. Narrate freely in third person, responding creatively to the player's actions.",
            inspiration_text,
            f"Player memory:\n{mem_text}" if mem_text else "",
            f"Player input:\n{player_input}",
            rule_guidance,
            "Encourage player creativity while making sure all actions respect D&D 5e rules. "
            "Do not force a linear story; let the player guide the adventure."
            "Include dialogue from NPCs naturally to enrich the narrative and make interactions vivid."
        ]
        prompt = "\n\n".join([p for p in prompt_parts if p])
        prompt = truncate_text(prompt)

        response = generate_response(prompt)

        add_event(player_id, event_type="player_input", description=player_input)
        add_event(player_id, event_type="dm_response", description=response)

        return response
