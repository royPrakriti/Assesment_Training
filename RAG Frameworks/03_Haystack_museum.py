
import shutil
from pathlib import Path

from haystack import Document, Pipeline

from haystack.components.preprocessors import DocumentSplitter
from haystack.components.writers import DocumentWriter

from haystack_integrations.components.embedders.sentence_transformers import (
    SentenceTransformersDocumentEmbedder,
    SentenceTransformersTextEmbedder
)

from haystack_integrations.components.retrievers.chroma import (
    ChromaEmbeddingRetriever
)

from haystack_integrations.document_stores.chroma import (
    ChromaDocumentStore
)


# ==========================================
# 1. PATH CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

DOCUMENTS_DIR = BASE_DIR / "Documents"
CHROMA_DIR = BASE_DIR / "chroma_haystack"

COLLECTION_NAME = "museum_haystack"


# ==========================================
# 2. READ TXT FILES
# ==========================================

txt_files = list(DOCUMENTS_DIR.glob("*.txt"))

if len(txt_files) != 2:
    raise ValueError(
        f"Expected exactly 2 txt files, found {len(txt_files)}"
    )

documents = []

for file_path in txt_files:

    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    document = Document(
        content=content,
        meta={
            "source": file_path.name,
            "file_name": file_path.name
        }
    )

    documents.append(document)

print(f"Loaded {len(documents)} documents successfully.")


# ==========================================
# 3. CREATE CHROMADB DOCUMENT STORE
# ==========================================

if CHROMA_DIR.exists():
    shutil.rmtree(CHROMA_DIR)

document_store = ChromaDocumentStore(
    collection_name=COLLECTION_NAME,
    persist_path=str(CHROMA_DIR),
    distance_function="cosine"
)


# ==========================================
# 4. CREATE INDEXING PIPELINE
# ==========================================

splitter = DocumentSplitter(
    split_by="word",
    split_length=150,
    split_overlap=20
)

document_embedder = SentenceTransformersDocumentEmbedder(
    model="sentence-transformers/all-MiniLM-L6-v2",
    normalize_embeddings=True
)

writer = DocumentWriter(
    document_store=document_store
)

indexing_pipeline = Pipeline()

indexing_pipeline.add_component(
    "splitter", splitter
)

indexing_pipeline.add_component(
    "embedder", document_embedder
)

indexing_pipeline.add_component(
    "writer", writer
)

# Connect pipeline components

indexing_pipeline.connect(
    "splitter.documents",
    "embedder.documents"
)

indexing_pipeline.connect(
    "embedder.documents",
    "writer.documents"
)


# ==========================================
# 5. RUN INDEXING PIPELINE
# ==========================================

indexing_pipeline.run(
    {
        "splitter": {
            "documents": documents
        }
    }
)

print("Chunks embedded and stored successfully.")

print("Total chunks:", document_store.count_documents())


# ==========================================
# 6. CREATE RETRIEVAL PIPELINE
# ==========================================

text_embedder = SentenceTransformersTextEmbedder(
    model="sentence-transformers/all-MiniLM-L6-v2",
    normalize_embeddings=True
)

retriever = ChromaEmbeddingRetriever(
    document_store=document_store,
    top_k=2
)

query_pipeline = Pipeline()

query_pipeline.add_component(
    "text_embedder", text_embedder
)

query_pipeline.add_component(
    "retriever", retriever
)

# Connect query embedding to retriever

query_pipeline.connect(
    "text_embedder.embedding",
    "retriever.query_embedding"
)

print("Retrieval pipeline created successfully.")


# ==========================================
# 7. RETRIEVAL
# ==========================================

while True:

    question = input(
        "\nEnter your question (or type 'exit'): "
    )

    if question.lower() == "exit":
        print("Exiting retrieval.")
        break

    results = query_pipeline.run(
        {
            "text_embedder": {
                "text": question
            }
        }
    )

    retrieved_documents = results["retriever"]["documents"]

    print("\n========== TOP 2 RETRIEVED CHUNKS ==========")

    for index, document in enumerate(
        retrieved_documents, start=1
    ):

        print(f"\nResult {index}")
        print("-" * 50)

        print(
            "Source File:",
            document.meta.get("source", "Unknown")
        )

        print(
            "Similarity Score:",
            round(document.score, 4)
            if document.score is not None else "N/A"
        )

        print("\nRetrieved Chunk:")
        print(document.content)

    print("\n============================================")
