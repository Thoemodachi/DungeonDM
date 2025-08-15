from .rag import retrieve_chunks, build_prompt
from .llm_client import generate_response
from .memory import add_event, get_recent_events, summarise_memory

def process_player_input(player_id, player_input, character_id=None):
    # 1. Retrieve relevant RAG chunks
    chunks = retrieve_chunks(player_input, top_k=5)

    # 2. Get recent memory
    recent_memory = get_recent_events(player_id, limit=10)
    memory_text = "\n".join([f"{e['type']}: {e['description']}" for e in recent_memory])

    # 3. Build full prompt
    prompt = build_prompt(player_input, chunks, character_id)
    full_prompt = memory_text + "\n" + prompt if memory_text else prompt

    # 4. Generate LLM response
    response = generate_response(full_prompt)

    # 5. Store event in memory
    add_event(player_id, event_type="player_input", description=player_input)
    add_event(player_id, event_type="dm_response", description=response)

    return response
