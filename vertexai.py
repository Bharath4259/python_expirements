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
