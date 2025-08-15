# ingest_dnd_pdfs_local_persistent_openai_logging.py
import os, uuid, re, json
import fitz
import chromadb
import openai
import numpy as np
from dotenv import load_dotenv

# Loads env variables in testing
load_dotenv()

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
openai.api_key = OPENAI_API_KEY
OPENAI_MODEL = "text-embedding-3-small"
CHUNK_SIZE = 700
CHUNK_OVERLAP = 100
PERSIST_DIR = "chroma_db"

# -------------------------
# INITIALIZE CHROMA
# -------------------------
client = chromadb.PersistentClient(path=PERSIST_DIR)
rules_col = client.get_or_create_collection(name="rules_and_refs")
campaign_col = client.get_or_create_collection(name="campaign")

# -------------------------
# HELPERS
# -------------------------

def extract_text_from_pdf(path: str) -> str:
    print(f"[INFO] Extracting text from PDF: {path}")
    doc = fitz.open(path)
    pages = [p.get_text() for p in doc]
    print(f"[INFO] Extracted {len(pages)} pages")
    return "\n".join(pages)

def clean_text(text: str) -> str:
    text = text.replace("\u2013","-").replace("\u2014","-")
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'Page \d+ of \d+', '', text, flags=re.I)
    return text.strip()

def chunk_text(text: str, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    chunks = []
    i = 0
    L = len(text)
    while i < L:
        end = min(i + chunk_size, L)
        chunk = text[i:end]
        if end < L:
            m = re.search(r'([\.!?])\s', text[end:end+50])
            if m:
                chunk = text[i:end + m.end()]
                end = i + len(chunk)
        chunks.append(chunk.strip())
        i = max(end - overlap, end) if end < L else end
    print(f"[INFO] Created {len(chunks)} chunks")
    return chunks

def embed_texts(texts, max_tokens=2000):
    embeddings = []
    print(f"[INFO] Embedding {len(texts)} text(s)")
    for idx, t in enumerate(texts):
        try:
            pieces = [t[i:i+max_tokens] for i in range(0, len(t), max_tokens)] if len(t) > max_tokens else [t]
            piece_embs = []
            for p in pieces:
                response = openai.embeddings.create(model=OPENAI_MODEL, input=p)
                piece_embs.append(response.data[0].embedding)
            if len(piece_embs) > 1:
                avg_emb = np.mean(piece_embs, axis=0).tolist()
                embeddings.append(avg_emb)
            else:
                embeddings.append(piece_embs[0])
        except Exception as e:
            print(f"[ERROR] Failed to embed chunk {idx}: {e}")
    print(f"[INFO] Generated {len(embeddings)} embeddings")
    return embeddings

# -------------------------
# MONSTER PARSER
# -------------------------
def parse_monster_statblock(text: str) -> dict:
    d = {}
    title = text.strip().split("\n")[0][:120]
    d["title"] = title
    def grab(field):
        m = re.search(rf'{field}[:\s]+(.+?)(?:\n[A-Z][a-zA-Z ]+?:|\n[A-Z ]{{2,}}:|$)', text, re.S|re.I)
        return m.group(1).strip() if m else None
    for f in ["Armor Class","Hit Points","Speed","STR","DEX","CON","INT","WIS","CHA","Actions","Special Abilities","Legendary Actions"]:
        v = grab(f)
        if v: d[f.lower().replace(" ","_")] = re.sub(r'\s+', ' ', v).strip()
    d["raw"] = text
    return d

# -------------------------
# DOCUMENT INDEXER
# -------------------------
def index_document(path, source, collection):
    text = extract_text_from_pdf(path)
    text = clean_text(text)
    doc_id = str(uuid.uuid4())
    print(f"[INFO] Indexing document {path} -> {doc_id}")

    if source.lower() in ("monster_manual","monster manual"):
        blocks = [b.strip() for b in re.split(r'\n{2,}', text) if len(b.strip())>50]
        structured_entries = []
        narrative_chunks = []
        for b in blocks:
            if "Armor Class" in b and ("Hit Points" in b or "Actions" in b):
                parsed = parse_monster_statblock(b)
                structured_entries.append(parsed)
            else:
                narrative_chunks.extend(chunk_text(b))
        # Index structured entries
        for idx, se in enumerate(structured_entries):
            summary = f"{se.get('title')}. AC: {se.get('armor_class','?')}. HP: {se.get('hit_points','?')}. Actions: {se.get('actions','')[:200]}"
            emb = embed_texts([summary])[0]
            meta = {"source":source,"doc_id":doc_id,"chunk_id":f"monster_{idx}","topic":"monster","title":se.get("title")}
            collection.add(documents=[summary], metadatas=[meta], ids=[f"{doc_id}_monster_{idx}"], embeddings=[emb])
            print(f"[INFO] Added monster chunk {idx}")
        # Index narrative chunks
        if narrative_chunks:
            embs = embed_texts(narrative_chunks)
            ids = [f"{doc_id}_chunk_{i}" for i in range(len(narrative_chunks))]
            metas = [{"source":source,"doc_id":doc_id,"chunk_id":i,"topic":"lore","title":narrative_chunks[i][:60]} for i in range(len(narrative_chunks))]
            collection.add(documents=narrative_chunks, metadatas=metas, ids=ids, embeddings=embs)
            print(f"[INFO] Added {len(narrative_chunks)} narrative chunks")
    else:
        chunks = chunk_text(text)
        embs = embed_texts(chunks)
        ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
        metas = [{"source":source,"doc_id":doc_id,"chunk_id":i,"topic":"campaign" if source=="campaign" else "rule","title":chunks[i][:60]} for i in range(len(chunks))]
        collection.add(documents=chunks, metadatas=metas, ids=ids, embeddings=embs)
        print(f"[INFO] Added {len(chunks)} chunks for {source}")

    # Verify total docs in collection after this document
    total_docs = len(collection.get(include=['documents'])['documents'])
    print(f"[INFO] Total documents in collection '{collection.name}': {total_docs}")


# -------------------------
# MAIN
# -------------------------
if __name__ == "__main__":
    INPUT_FILES = [
        ("data/A_GREAT_UPHEAVAL.pdf","campaign"),
        ("data/DnD_5e_Players_Handbook.pdf","phb"),
        ("data/Dungeon_Masters_Guide.pdf","dmg"),
        ("data/Monster_Manual.pdf","monster_manual"),
        ("data/SRD.pdf","srd")
    ]
    for path, src in INPUT_FILES:
        if os.path.exists(path):
            target_col = campaign_col if src=="campaign" else rules_col
            index_document(path, src, target_col)
        else:
            print(f"[WARNING] Missing file {path}")

    # Final verification
    print(f"[INFO] Final document counts:")
    print(f"  rules_and_refs: {len(rules_col.get(include=['documents'])['documents'])}")
    print(f"  campaign: {len(campaign_col.get(include=['documents'])['documents'])}")
    print(f"[INFO] Chroma DB persisted to {PERSIST_DIR}")
