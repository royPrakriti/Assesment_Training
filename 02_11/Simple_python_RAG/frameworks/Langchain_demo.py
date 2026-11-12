#langchain manually done
from pathlib import Path
import sys

# Import rag_core.py from our existing project
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

from rag_core import (
    DB_PATH,
    DOCUMENT_PATH,
    read_document,
    embed_texts,
    get_database,
)

COLLECTION = "langchain_brightpath"


# Reuse our existing local embedding model
class LocalEmbeddings(Embeddings):

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return embed_texts(texts)

    def embed_query(self, text: str) -> list[float]:
        return embed_texts([text])[0]


# STEP 1: READ DOCUMENT
source = str(DOCUMENT_PATH.relative_to(PROJECT_ROOT))

documents = [
    Document(
        page_content=read_document(),
        metadata={"source": source}
    )
]

print("Document loaded:", source)


# STEP 2: CHUNK DOCUMENT
splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    encoding_name="cl100k_base",
    chunk_size=180,
    chunk_overlap=35
)

chunks = splitter.split_documents(documents)

for i, chunk in enumerate(chunks, start=1):
    chunk.metadata["chunk_id"] = f"lc_chunk_{i:03d}"

print("Total chunks:", len(chunks))
print("First chunk:", chunks[0].page_content[:130])


# STEP 3: STORE IN CHROMADB
client = get_database()

# Use a separate collection to protect our original data
if COLLECTION in [item.name for item in client.list_collections()]:
    client.delete_collection(COLLECTION)

store = Chroma.from_documents(
    documents=chunks,
    embedding=LocalEmbeddings(),
    collection_name=COLLECTION,
    persist_directory=str(DB_PATH),
    collection_configuration={"hnsw": {"space": "cosine"}}
)

print("Stored chunks:", client.get_collection(COLLECTION).count())


# STEP 4: SEARCH AND RETRIEVE
while True:
    question = input("\nEnter your question (exit to stop): ").strip()

    if question.lower() == "exit":
        break

    if not question:
        continue

    results = store.similarity_search_with_score(question, k=3)

    for document, distance in results:
        print("\n" + "-" * 60)
        print("Chunk:", document.metadata["chunk_id"])
        print("Source:", document.metadata["source"])
        print("Cosine distance:", round(distance, 4))
        print("Text:", document.page_content)