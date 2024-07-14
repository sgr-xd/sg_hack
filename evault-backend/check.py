import os
from google.cloud import storage

# Path to your service account key file
service_account_key_path = 'upheld-castle-429321-c2-f44b1b00aff8.json'

# Set the environment variable for Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = service_account_key_path

# Initialize a client with the service account credentials
storage_client = storage.Client()

# Test the client by listing buckets
buckets = list(storage_client.list_buckets())
print("Buckets:")
for bucket in buckets:
    print(bucket.name)