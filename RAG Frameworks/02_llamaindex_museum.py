
import shutil
from pathlib import Path

import chromadb

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext


# ==========================================
# 1. PATH CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

DOCUMENTS_DIR = BASE_DIR / "Documents"
CHROMA_DIR = BASE_DIR / "chroma_llamaindex"

COLLECTION_NAME = "museum_llamaindex"


# ==========================================
# 2. LOAD TXT FILES
# ==========================================

txt_files = list(DOCUMENTS_DIR.glob("*.txt"))

if len(txt_files) != 2:
    raise ValueError(
        f"Expected exactly 2 txt files, found {len(txt_files)}"
    )

documents = SimpleDirectoryReader(
    input_files=[str(file) for file in txt_files],
    filename_as_id=True
).load_data()

print(f"Loaded {len(documents)} documents successfully.")


# ==========================================
# 3. SPLIT DOCUMENTS INTO NODES
# ==========================================

splitter = SentenceSplitter(
    chunk_size=150,
    chunk_overlap=20
)

nodes = splitter.get_nodes_from_documents(documents)

print(f"Total chunks created: {len(nodes)}")


# ==========================================
# 4. LOAD LOCAL EMBEDDING MODEL
# ==========================================

embedding_model = HuggingFaceEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    device="cpu",
    normalize=True
)

print("Local embedding model loaded successfully.")


# ==========================================
# 5. CREATE CHROMADB COLLECTION
# ==========================================

if CHROMA_DIR.exists():
    shutil.rmtree(CHROMA_DIR)

chroma_client = chromadb.PersistentClient(
    path=str(CHROMA_DIR)
)

collection = chroma_client.get_or_create_collection(
    name=COLLECTION_NAME
)

vector_store = ChromaVectorStore(
    chroma_collection=collection
)

storage_context = StorageContext.from_defaults(
    vector_store=vector_store
)


# ==========================================
# 6. CREATE VECTOR INDEX
# ==========================================

index = VectorStoreIndex(
    nodes=nodes,
    storage_context=storage_context,
    embed_model=embedding_model
)

print("Chunks stored in ChromaDB successfully.")
print(f"Collection: {COLLECTION_NAME}")


# ==========================================
# 7. RETRIEVAL
# ==========================================

retriever = index.as_retriever(
    similarity_top_k=2
)

while True:

    question = input("\nEnter your question (or type 'exit'): ")

    if question.lower() == "exit":
        print("Exiting retrieval.")
        break

    results = retriever.retrieve(question)

    print("\n========== TOP 2 RETRIEVED CHUNKS ==========")

    for index_number, result in enumerate(results, start=1):

        print(f"\nResult {index_number}")
        print("-" * 50)

        print(
            "Source File:",
            result.node.metadata.get("file_name", "Unknown")
        )

        print("Similarity Score:", round(result.score, 4))

        print("\nRetrieved Chunk:")
        print(result.node.text)

    print("\n============================================")
