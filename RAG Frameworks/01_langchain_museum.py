
import os
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


# ==========================================
# 1. PATH CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent
DOCUMENTS_DIR = BASE_DIR / "Documents"
CHROMA_DIR = BASE_DIR / "chroma_db"

COLLECTION_NAME = "museum_langchain"


# ==========================================
# 2. READ TXT FILES AND CREATE DOCUMENTS
# ==========================================

documents = []

txt_files = list(DOCUMENTS_DIR.glob("*.txt"))

if len(txt_files) != 2:
    raise ValueError(
        f"Expected exactly 2 txt files in Documents/, found {len(txt_files)}"
    )

for file_path in txt_files:

    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()

    document = Document(
        page_content=text,
        metadata={
            "source": file_path.name
        }
    )

    documents.append(document)

print(f"Loaded {len(documents)} documents successfully.")


# ==========================================
# 3. SPLIT DOCUMENTS INTO CHUNKS
# ==========================================

text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=150,
    chunk_overlap=20,
    encoding_name="cl100k_base"
)

chunks = text_splitter.split_documents(documents)

print(f"Total chunks created: {len(chunks)}")


# ==========================================
# 4. LOAD LOCAL EMBEDDING MODEL
# ==========================================

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={
        "device": "cpu"
    },
    encode_kwargs={
        "normalize_embeddings": True
    }
)

print("Local embedding model loaded successfully.")


# ==========================================
# 5. STORE CHUNKS IN CHROMADB
# ==========================================

# Rebuild the collection for a fresh ingestion.
if CHROMA_DIR.exists():
    import shutil
    shutil.rmtree(CHROMA_DIR)

vector_store = Chroma.from_documents(
    documents=chunks,
    embedding=embedding_model,
    collection_name=COLLECTION_NAME,
    persist_directory=str(CHROMA_DIR)
)

print("Chunks stored in ChromaDB successfully.")
print(f"Collection: {COLLECTION_NAME}")


# ==========================================
# 6. RETRIEVAL
# ==========================================

while True:

    question = input("\nEnter your question (or type 'exit'): ")

    if question.lower() == "exit":
        print("Exiting retrieval.")
        break

    results = vector_store.similarity_search_with_score(
        query=question,
        k=2
    )

    print("\n========== TOP 2 RETRIEVED CHUNKS ==========")

    for index, (document, distance) in enumerate(results, start=1):

        print(f"\nResult {index}")
        print("-" * 50)

        print("Source File:", document.metadata.get("source"))
        print("Distance:", round(distance, 4))

        print("\nRetrieved Chunk:")
        print(document.page_content)

    print("\n============================================")
