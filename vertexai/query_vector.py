from google.cloud import aiplatform_v1
 
# Set variables for the current deployed index.
API_ENDPOINT="2060605935.europe-west2-441337251459.vdb.vertexai.goog"
INDEX_ENDPOINT="projects/441337251459/locations/europe-west2/indexEndpoints/6739249814266970112"
DEPLOYED_INDEX_ID="embedding_api_stream_index_1722404973889"
 
# Configure Vector Search client
client_options = {
  "api_endpoint": API_ENDPOINT
}
vector_search_client = aiplatform_v1.MatchServiceClient(
  client_options=client_options,
)
 
# Build FindNeighborsRequest object
datapoint = aiplatform_v1.IndexDatapoint(
  feature_vector="<FEATURE_VECTOR>"
)
 
query = aiplatform_v1.FindNeighborsRequest.Query(
  datapoint=datapoint,
 
  # The number of nearest neighbors to be retrieved
  neighbor_count=10
)
request = aiplatform_v1.FindNeighborsRequest(
  index_endpoint=INDEX_ENDPOINT,
  deployed_index_id=DEPLOYED_INDEX_ID,
  # Request can have multiple queries
  queries=[query],
  return_full_datapoint=False,
)
 
# Execute the request
response = vector_search_client.find_neighbors(request)
 
# Handle the response
print(response)