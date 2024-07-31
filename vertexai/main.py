import subprocess  # nosec
from google.cloud import aiplatform  # nosec
 
 
def setup_environment():
    global PROJECT_ID, REGION, BUCKET_URI, DIMENSIONS, DISPLAY_NAME, VPC_NETWORK_FULL
    PROJECT_ID = "dpduk-p-aibot-d1"
    REGION = "europe-west2"
    BUCKET_URI = "gs://dpd_rag_vertex_ai"
    DIMENSIONS = 768
    DISPLAY_NAME = "dpd-straive"
 
 
def run_gcloud_command():
    gcloud_command = [
        "gcloud",
        "projects",
        "list",
        f"--filter=PROJECT_ID:'{PROJECT_ID}'",
        "--format=value(PROJECT_NUMBER)",
    ]
    process = subprocess.run(gcloud_command, capture_output=True, text=True)  # nosec
    if process.returncode != 0:
        exit()
    return process.stdout.strip()
 
 
def init_ai_platform(project_id, region, bucket_uri):
    aiplatform.init(
        project=project_id, location=region, staging_bucket=bucket_uri)
 
 
def create_brute_force_index(display_name, bucket_uri, dimensions):
    return aiplatform.MatchingEngineIndex.create_brute_force_index(
        display_name=display_name,
        contents_delta_uri=bucket_uri,
        dimensions=dimensions,
        distance_measure_type="COSINE_DISTANCE",
    )
 
 
def create_index_endpoint(display_name):
    return aiplatform.MatchingEngineIndexEndpoint.create(
        display_name=display_name, public_endpoint_enabled=True
    )
 
 
def deploy_index_to_endpoint(index_endpoint, index, deployed_index_id):
    index_endpoint.deploy_index(index=index, deployed_index_id=deployed_index_id)
 
 
def main():
    setup_environment()
    project_number = run_gcloud_command()
    global VPC_NETWORK_FULL
    VPC_NETWORK_FULL = f"projects/{project_number}/global/networks/default"
 
    init_ai_platform(PROJECT_ID, REGION, BUCKET_URI)
 
    my_index = create_brute_force_index(DISPLAY_NAME, BUCKET_URI, DIMENSIONS)
 
    my_index_endpoint = create_index_endpoint("smoke_test")
 
    deploy_index_to_endpoint(my_index_endpoint, my_index, "smoke_test")
 
 
if __name__ == "__main__":
    main()
 