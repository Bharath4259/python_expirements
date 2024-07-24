pip install langchain google-cloud-aiplatform weaviate-client PyMuPDF

2. Set up Google Cloud Vertex AI and ensure you have the necessary permissions and API key.

3. Set up a vector database in GCP (e.g., Weaviate) and get the endpoint URL.

Python Program:

```
import os
import fitz  # PyMuPDF
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_vertexai import VertexAIEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.vectorstores import Chroma
import chromadb
from chromadb.config import Settings

import vertexai


# Set up Google Cloud Vertex AI API key and project details
api_key = "your-google-cloud-api-key"
project_id = "your-google-cloud-project-id"
location = "your-google-cloud-location"  # e.g., "us-central1"

# Set up Google Cloud Vertex AI API key
os.environ["GOOGLE_CLOUD_API_KEY"] = "your-google-cloud-api-key"


# Initialize Vertex AI
vertexai.init(project=project_id, location=location, credentials=api_key)


# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# Initialize the text splitter
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

# Initialize Vertex AI Embeddings
# vertex_ai_embeddings = VertexAIEmbeddings(api_key=os.getenv("GOOGLE_CLOUD_API_KEY"))

# Initialize Vertex AI Embeddings
vertex_ai_embeddings = VertexAIEmbeddings(api_key=api_key)


# Initialize ChromaDB client
chroma_client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory="./chroma_db"))

# Function to process a PDF document and store embeddings
def process_pdf_and_store_embeddings(pdf_path):
    # Extract text from PDF
    text = extract_text_from_pdf(pdf_path)
    
    # Split text into chunks
    chunks = text_splitter.split_text(text)
    
    # Create embeddings for each chunk
    embeddings = [vertex_ai_embeddings.embed(chunk) for chunk in chunks]
    
    # Store embeddings in ChromaDB
    collection = chroma_client.get_or_create_collection(name="pdf_texts")
    for chunk, embedding in zip(chunks, embeddings):
        collection.add(
            documents=[{
                "id": str(hash(chunk)),
                "embedding": embedding,
                "metadata": {"text": chunk}
            }]
        )

# Function to create a Q&A system
def create_qa_system(pdf_paths):
    # Process each PDF and store embeddings
    for pdf_path in pdf_paths:
        process_pdf_and_store_embeddings(pdf_path)
    
    # Initialize Chroma VectorStore
    collection = chroma_client.get_collection(name="pdf_texts")
    chroma_store = Chroma(client=chroma_client, collection=collection)
    
    # Initialize ConversationalRetrievalChain
    qa_chain = ConversationalRetrievalChain(
        retriever=chroma_store.as_retriever(),
        llm="your-llm-model",  # Replace with the appropriate language model
        verbose=True
    )
    
    return qa_chain

# List of PDF documents
pdf_paths = [
    "path/to/your/document1.pdf",
    "path/to/your/document2.pdf",
    # Add more PDF paths as needed
]

# Create the Q&A system
qa_system = create_qa_system(pdf_paths)

# Example usage
question = "What is the RDQ Operational Data Strategy?"
answer = qa_system.ask(question)
print(f"Q: {question}\nA: {answer}")

```
