###Enable Google Cloud APIs and login with your credentials
#gcloud services enable compute.googleapis.com aiplatform.googleapis.com storage.googleapis.com
#gcloud auth application-default login

###Install required Python modules
#pip install pypdf2
#pip install google-cloud-storage
#pip install google-cloud-aiplatform
#pip install jupyter

from google.cloud import storage
from vertexai.language_models import TextEmbeddingModel
from google.cloud import aiplatform

import PyPDF2

import re
import os
import random
import json
import uuid

project="your_GCP_project_id"
location="us-central1"

pdf_path="lakeside_handbook.pdf"
bucket_name = "lakeside-content"
embed_file_path = "lakeside_embeddings.json"
sentence_file_path = "lakeside_sentences.json"
index_name="lakeside_index"

def extract_sentences_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            if page.extract_text() is not None:
                text += page.extract_text() + " "
    sentences = [sentence.strip() for sentence in text.split('. ') if sentence.strip()]
    return sentences

def generate_text_embeddings(sentences) -> list: 
  aiplatform.init(project=project,location=location)
  model = TextEmbeddingModel.from_pretrained("textembedding-gecko@001")
  embeddings = model.get_embeddings(sentences)
  vectors = [embedding.values for embedding in embeddings]
  return vectors

def generate_and_save_embeddings(pdf_path, sentence_file_path, embed_file_path):
    def clean_text(text):
        cleaned_text = re.sub(r'\u2022', '', text)  # Remove bullet points
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()  # Remove extra whitespaces and strip
        return cleaned_text
    
    sentences = extract_sentences_from_pdf(pdf_path)
    if sentences:
        embeddings = generate_text_embeddings(sentences)
        
        with open(embed_file_path, 'w') as embed_file, open(sentence_file_path, 'w') as sentence_file:
            for sentence, embedding in zip(sentences, embeddings):
                cleaned_sentence = clean_text(sentence)
                id = str(uuid.uuid4())
                
                embed_item = {"id": id, "embedding": embedding}
                sentence_item = {"id": id, "sentence": cleaned_sentence}
                
                json.dump(sentence_item, sentence_file)
                sentence_file.write('\n') 
                json.dump(embed_item, embed_file)
                embed_file.write('\n')  

def upload_file(bucket_name,file_path):
    storage_client = storage.Client()
    bucket = storage_client.create_bucket(bucket_name,location=location)
    blob = bucket.blob(file_path)
    blob.upload_from_filename(file_path)
    
def create_vector_index(bucket_name, index_name):
    lakeside_index = aiplatform.MatchingEngineIndex.create_tree_ah_index(
    display_name = index_name,
    contents_delta_uri = "gs://"+bucket_name,
    dimensions = 768,
    approximate_neighbors_count = 10,
    )
                  
    lakeside_index_endpoint = aiplatform.MatchingEngineIndexEndpoint.create(
    display_name = index_name,
    public_endpoint_enabled = True
    )                      

    lakeside_index_endpoint.deploy_index(
    index = lakeside_index, deployed_index_id = index_name
    )

generate_and_save_embeddings(pdf_path,sentence_file_path,embed_file_path)
upload_file(bucket_name,file_path)
create_vector_index(bucket_name, index_name)
