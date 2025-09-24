import os
from pathlib import Path
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# ==============================
# Config
# ==============================
EMBEDDER_MODEL = os.getenv("EMBEDDER_MODEL", "all-MiniLM-L6-v2")
CHROMA_PATH = Path("rag/chroma")  # dossier où Chroma va persister les données
CHROMA_PATH.mkdir(parents=True, exist_ok=True)

# ==============================
# Initialisation du client
# ==============================
_chroma_server = os.getenv("CHROMA_SERVER_URL", "").strip()

if _chroma_server:
    # Connexion à un serveur Chroma externe (REST)
    client = chromadb.Client(Settings(
        chroma_api_impl="rest",
        chroma_server_host=_chroma_server.replace("http://", "").split(":")[0],
        chroma_server_http_port=_chroma_server.split(":")[-1] if ":" in _chroma_server else "8000",
    ))
else:
    # Stockage persistant en local
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))

collection = client.get_or_create_collection(name="css_docs")

# ==============================
# Embeddings
# ==============================
_embedder = SentenceTransformer(EMBEDDER_MODEL)

def embed_texts(texts: list[str]):
    """Convertit une liste de textes en embeddings."""
    return _embedder.encode(texts, show_progress_bar=False).tolist()

# ==============================
# Insertion / mise à jour
# ==============================
def upsert_chunks(chunks: list[dict]):
    """
    Insère des chunks dans Chroma.
    Chaque chunk doit être un dict : {"id": str, "text": str, "meta": dict}
    """
    if not chunks:
        print("[Chroma] Aucun chunk à insérer.")
        return

    texts = [c["text"] for c in chunks]
    ids = [c["id"] for c in chunks]
    metas = [c.get("meta", {}) for c in chunks]
    embeddings = embed_texts(texts)

    collection.add(ids=ids, embeddings=embeddings, metadatas=metas, documents=texts)
    print(f"[Chroma] Ajouté {len(texts)} chunks. Total docs: {collection.count()}")

# ==============================
# Recherche
# ==============================
def retrieve(query: str, top_k: int = 5):
    """
    Recherche les passages les plus pertinents dans la base Chroma.
    """
    emb = embed_texts([query])[0]
    results = collection.query(query_embeddings=[emb], n_results=top_k)
    return results
