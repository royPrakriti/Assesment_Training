
import os
import chromadb
import tiktoken
from sentence_transformers import SentenceTransformer
from groq import Groq
from dotenv import load_dotenv

# Load API key
load_dotenv()

groq_client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# Load models
model = SentenceTransformer("all-MiniLM-L6-v2")
tokenizer = tiktoken.get_encoding("cl100k_base")


# TASK 1: READ AND TOKENIZE DOCUMENTS

document_folder = "documents"
documents = []

for filename in os.listdir(document_folder):

    if filename.endswith(".txt"):

        path = os.path.join(document_folder, filename)

        with open(path, "r", encoding="utf-8") as f:

            documents.append({
                "text": f.read(),
                "source": filename
            })


for doc in documents:

    print("\nFile:", doc["source"])
    print("\nDocument Content:")
    print(doc["text"])

    tokens = tokenizer.encode(doc["text"])

    print("\nTotal Tokens:", len(tokens))
    print("-" * 50)


# TASK 2: CHUNK DOCUMENTS

all_chunks = []

for doc in documents:

    tokens = tokenizer.encode(doc["text"])

    chunks = []
    start = 0

    while start < len(tokens):

        chunk_tokens = tokens[start:start + 120]

        chunk_text = tokenizer.decode(chunk_tokens)

        chunks.append(chunk_text)

        start += 100

    all_chunks.append({
        "source": doc["source"],
        "chunks": chunks
    })


# Display total chunks and sample chunk

total_chunks = 0

for doc in all_chunks:

    total_chunks += len(doc["chunks"])

    if doc["chunks"]:
        sample_chunk = doc["chunks"][0]

print("\nTotal Chunks:", total_chunks)

if total_chunks > 0:
    print("\nSample Chunk:", sample_chunk)


# GENERATE EMBEDDINGS

texts = []

for doc in all_chunks:
    texts.extend(doc["chunks"])

if not texts:
    raise ValueError("No text chunks found in documents folder.")

embeddings = model.encode(texts)

print("\nEmbeddings generated successfully!")
print("Vector size:", embeddings.shape[1])
print("Embedding shape:", embeddings.shape)


# TASK 3: STORE IN CHROMADB

client = chromadb.PersistentClient(
    path="./chroma_db"
)

# Delete old collection if it exists

try:
    client.delete_collection(name="documents")
except Exception:
    pass

# Create collection

collection = client.create_collection(
    name="documents",
    metadata={"hnsw:space": "cosine"}
)

# Prepare data

stored_texts = []
metadatas = []

for doc in all_chunks:

    for chunk in doc["chunks"]:

        stored_texts.append(chunk)

        metadatas.append({
            "source": doc["source"]
        })


# Store chunks and embeddings

collection.add(
    ids=[str(i) for i in range(len(stored_texts))],
    documents=stored_texts,
    embeddings=embeddings.tolist(),
    metadatas=metadatas
)

print("\nChunks stored successfully in ChromaDB!")


# ASK QUESTION

question = input("\nEnter your question: ")

# Generate question embedding

question_embedding = model.encode(question)

# Retrieve top 4 chunks

results = collection.query(
    query_embeddings=[question_embedding.tolist()],
    n_results=min(4, len(stored_texts))
)


# Display retrieved chunks

print("\nTop Retrieved Chunks:")

for i in range(len(results["documents"][0])):

    print(f"\nResult {i+1}")

    print("Source:", results["metadatas"][0][i]["source"])

    print("Chunk:", results["documents"][0][i])

    print("Cosine Distance:", results["distances"][0][i])


# TASK 4: GROQ LLM ANSWER GENERATION

# Combine retrieved context

context = "\n\n".join(results["documents"][0])

response = groq_client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[
        {
            "role": "system",
            "content": """
            Answer only from the provided context.
            Do not display or repeat the context.
            Do not list the retrieved chunks.
            If the answer is unavailable, say:
            I cannot find the answer in the provided documents.
            """
        },
        {
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion: {question}"
        }
    ],
    temperature=0
)

print("\nAI Answer:")
print(response.choices[0].message.content)



