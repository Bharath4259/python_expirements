import pandas as pd
import json
import ast
from vertexai.preview.language_models import TextEmbeddingModel
 
model_name = "textembedding-gecko@001"
model = TextEmbeddingModel.from_pretrained(model_name)
 
def text_embedding(text):
    embeddings = model.get_embeddings([text])
    return [str(embedding.values) for embedding in embeddings]
 
def process_csv_to_embeddings_json(input_csv_path, output_json_path, output_json_matching_path):
    # Reading the CSV file
    data = pd.read_csv(input_csv_path, encoding='latin1')
 
    doc_data_list = []
    matching_doc_data_list = []
 
    for index, row in data.iterrows():
        print(index)
        # Process the content to get the embedding
        embedding = text_embedding(row['content'])[0]
        embedding_list = ast.literal_eval(str(embedding))
        embedding_strings = [str(value) for value in embedding_list]
       
        doc_data = {
            "id": str(index),
            "embedding": embedding_strings,
        }
        matching_doc_data = {
            "id": f"identity{index}",
            "type": row['type'],
            "embedding": row['content'],
            "context_block": row['context_block']
        }
 
        doc_data_list.append(doc_data)
        matching_doc_data_list.append(matching_doc_data)
 
    # Write the document data to the JSON file
    with open(output_json_path, 'w', encoding='utf-8') as json_file:
        for doc_data in doc_data_list:
            json.dump(doc_data, json_file)
            json_file.write('\n')
 
    with open(output_json_matching_path, 'w', encoding='utf-8') as json_file:
        for matching_doc_data in matching_doc_data_list:
            json.dump(matching_doc_data, json_file)
            json_file.write('\n')
 
# Example usage
input_csv_path = "embeddings_20240627_110000.csv"  # Replace with your actual file path
output_json_path = 'chatdpd_llm_rag__20240627_110000.json'
output_json_matching_path = 'chatdpd_llm_rag_matching_file_20240627_110000.json'
process_csv_to_embeddings_json(input_csv_path, output_json_path, output_json_matching_path)

# Format for JSON
# doc_data = {
#     "id": str(index),
#     "embedding": embedding_strings,
# }
