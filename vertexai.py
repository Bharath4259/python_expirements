import PyPDF2
import re
from google.oauth2 import service_account
from google.cloud import aiplatform
from google.cloud import aiplatform_v1
from google.cloud.aiplatform_v1.types import PredictRequest
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
import numpy as np

# Authenticate
service_account_path = 'path_to_your_service_account_key.json'
credentials = service_account.Credentials.from_service_account_file(service_account_path)
aiplatform.init(credentials=credentials)

# Extract text from PDFs
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfFileReader(file)
        text = ''
        for page_num in range(reader.numPages):
            page = reader.getPage(page_num)
            text += page.extract_text()
    return text

# Preprocess text
def preprocess_text(text):
    text = re.sub(r'\W+', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip().lower()
    tokens = text.split()
    tokens = [token for token in tokens if token not in ENGLISH_STOP_WORDS]
    return ' '.join(tokens)

pdf_paths = ['file1.pdf', 'file2.pdf', 'file3.pdf']
texts = [extract_text_from_pdf(path) for path in pdf_paths]
preprocessed_texts = [preprocess_text(text) for text in texts]

# Create embeddings with batch processing
def create_embeddings(texts, model_name='your_model_name', batch_size=5):
    client = aiplatform_v1.PredictionServiceClient(credentials=credentials)
    project = 'your_project_id'
    location = 'us-central1'
    endpoint = client.endpoint_path(project=project, location=location, endpoint=model_name)
    embeddings = []
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i+batch_size]
        instances = [{'content': text} for text in batch_texts]
        request = PredictRequest(endpoint=endpoint, instances=instances)
        response = client.predict(request=request)
        embeddings.extend(response.predictions)
    return embeddings

embeddings = create_embeddings(preprocessed_texts)
embeddings = np.array(embeddings)

# Output the embeddings
for i, embedding in enumerate(embeddings):
    print(f'Embedding for {pdf_paths[i]}: {embedding}')


# -----------------------------------------------------------------------------


import PyPDF2
import re
from google.oauth2 import service_account
from google.cloud import aiplatform
from langchain.embeddings import VertexAIEmbeddings
from langchain.vectorstores import FAISS

# Authenticate
service_account_path = 'path_to_your_service_account_key.json'
credentials = service_account.Credentials.from_service_account_file(service_account_path)
aiplatform.init(credentials=credentials)

# Extract text from PDFs
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfFileReader(file)
        text = ''
        for page_num in range(reader.numPages):
            page = reader.getPage(page_num)
            text += page.extract_text()
    return text

# Preprocess text
def preprocess_text(text):
    text = re.sub(r'\W+', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip().lower()
    return text

pdf_paths = ['file1.pdf', 'file2.pdf', 'file3.pdf']
texts = [extract_text_from_pdf(path) for path in pdf_paths]
preprocessed_texts = [preprocess_text(text) for text in texts]

# Define your model and initialize embeddings
vertex_model = VertexAIEmbeddings(
    model_name='your_model_name',
    project='your_project_id',
    location='us-central1',
    credentials=credentials
)

# Generate embeddings
def create_embeddings(texts, embeddings_model):
    return [embeddings_model.embed_text(text) for text in texts]

embeddings = create_embeddings(preprocessed_texts, vertex_model)

# Store embeddings in FAISS vector store for efficient retrieval
vector_store = FAISS.from_texts(preprocessed_texts, embeddings, vertex_model)

# Output the embeddings
for i, embedding in enumerate(embeddings):
    print(f'Embedding for {pdf_paths[i]}: {embedding}')


# -------------------------------------------------------------------------------------

from google.cloud.aiplatform_v1.types import PredictRequest
import numpy as np
from langchain.vectorstores import FAISS
from langchain.embeddings import Embeddings

# ... common code ...

# Define a function to generate embeddings using Vertex AI
def create_embeddings(texts, project_id, model_name, location, credentials):
    client = aiplatform_v1.PredictionServiceClient(credentials=credentials)
    endpoint = client.endpoint_path(project=project_id, location=location, endpoint=model_name)

    embeddings = []
    for text in texts:
        instances = [{'content': text}]
        request = PredictRequest(endpoint=endpoint, instances=instances)
        response = client.predict(request=request)
        embeddings.extend([pred for pred in response.predictions])
    
    return embeddings

# Generate embeddings
embeddings = create_embeddings(preprocessed_texts, 'your_project_id', 'your_model_name', 'us-central1', credentials)

# Convert embeddings to numpy array for better handling
embeddings = np.array(embeddings)

# Define a custom embeddings class
class CustomEmbeddings(Embeddings):
    def __init__(self, embeddings):
        self.embeddings = embeddings

    def embed_text(self, text):
        index = preprocessed_texts.index(text)
        return self.embeddings[index]

# Initialize the custom embeddings class
custom_embeddings = CustomEmbeddings(embeddings)

# Store embeddings in FAISS vector store for efficient retrieval
vector_store = FAISS.from_texts(preprocessed_texts, custom_embeddings)

# Output the embeddings
for i, embedding in enumerate(embeddings):
    print(f'Embedding for {pdf_paths[i]}: {embedding}')

# -----------------------------------------------------------------------------------------------------


import PyPDF2
import re
import numpy as np
from google.oauth2 import service_account
from google.cloud import aiplatform
from google.cloud import aiplatform_v1
from google.cloud.aiplatform_v1.types import PredictRequest

# Authentication
service_account_path = 'path_to_your_service_account_key.json'
credentials = service_account.Credentials.from_service_account_file(service_account_path)
aiplatform.init(credentials=credentials)

# Extract text from PDFs
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfFileReader(file)
        text = ''
        for page_num in range(reader.numPages):
            page = reader.getPage(page_num)
            text += page.extract_text()
    return text

# Preprocess text
def preprocess_text(text):
    text = re.sub(r'\W+', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip().lower()
    return text

pdf_paths = ['file1.pdf', 'file2.pdf', 'file3.pdf']
texts = [extract_text_from_pdf(path) for path in pdf_paths]
preprocessed_texts = [preprocess_text(text) for text in texts]

# Function to generate embeddings using Vertex AI
def create_embeddings(texts, project_id, model_name, location, credentials):
    client = aiplatform_v1.PredictionServiceClient(credentials=credentials)
    endpoint = client.endpoint_path(project=project_id, location=location, endpoint=model_name)

    embeddings = []
    for text in texts:
        instances = [{'content': text}]
        request = PredictRequest(endpoint=endpoint, instances=instances)
        response = client.predict(request=request)
        embeddings.extend([pred for pred in response.predictions])
    
    return np.array(embeddings)

# Generate embeddings
embeddings = create_embeddings(preprocessed_texts, 'your_project_id', 'your_model_name', 'us-central1', credentials)

# Function to update embeddings to Google Vector Search
from google.cloud import aiplatform_v1beta1 as aiplatform
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value

def update_embeddings_to_vector_search(
    project_id, location, index_id, embeddings, doc_ids
):
    # Initialize the Vertex AI Matching Engine client
    client = aiplatform.MatchServiceClient()

    # Define the parent path for the index
    index_name = client.index_path(project_id, location, index_id)

    # Create a list of index items (each containing an embedding and the corresponding doc ID)
    index_items = [
        aiplatform.IndexItem(
            id=doc_id,
            embedding=embedding.tolist(),  # Convert numpy array to list
            # Optionally, add any additional metadata
            metadata=json_format.ParseDict({"doc_id": doc_id}, Value()),
        )
        for doc_id, embedding in zip(doc_ids, embeddings)
    ]

    # Define the request
    request = aiplatform.UpsertIndexItemsRequest(
        index=index_name,
        index_items=index_items,
    )

    # Execute the request
    response = client.upsert_index_items(request=request)
    print(f"Upserted {len(index_items)} items into index {index_id}.")

# Example usage
project_id = 'your_project_id'
location = 'us-central1'
index_id = 'your_index_id'
doc_ids = [f'doc{i}' for i in range(len(preprocessed_texts))]

update_embeddings_to_vector_search(project_id, location, index_id, embeddings, doc_ids)

# ---------------------------------------------------------------------------------------------------------------

import os
import pandas as pd
from google.cloud import aiplatform

def upload_embeddings_to_vertex_ai(embeddings, metadata, project_id, location, index_endpoint_name):
  """Uploads embeddings and metadata to Vertex AI Vector Search.

  Args:
    embeddings: A list of numpy arrays, each representing an embedding.
    metadata: A list of dictionaries, each containing metadata for an embedding.
    project_id: Your Google Cloud project ID.
    location: The location of your Vertex AI instance.
    index_endpoint_name: The name of your Vertex AI Vector Search index endpoint.
  """

  # Create a client
  aiplatform.init(project=project_id, location=location)

  # Prepare data for upload
  data = []
  for embedding, meta in zip(embeddings, metadata):
    data.append({
      "embeddings": embedding.tolist(),
      "metadata": meta
    })

  # Create a pandas DataFrame from the data
  df = pd.DataFrame(data)

  # Upload data to Vertex AI Vector Search
  index_endpoint = aiplatform.IndexEndpoint(index_endpoint_name)
  index_endpoint.upload_data(df)

# Example usage:
embeddings = [embedding1, embedding2, ...]  # Replace with your embeddings
metadata = [{"id": 1, "title": "Document 1"}, {"id": 2, "title": "Document 2"}, ...]  # Replace with your metadata
project_id = "your-project-id"
location = "us-central1"
index_endpoint_name = "your-index-endpoint-name"

upload_embeddings_to_vertex_ai(embeddings, metadata, project_id, location, index_endpoint_name)


# ---------------------------------------------------------------------------------------------------------------




