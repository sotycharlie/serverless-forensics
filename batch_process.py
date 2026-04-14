import boto3
import json
import time

s3 = boto3.client('s3')
lambda_client = boto3.client('lambda')
BUCKET = "phi-ingestion-bucket-sotonye1"

print("Getting list of files...")
response = s3.list_objects_v2(Bucket=BUCKET, Prefix="incoming/")
files = response.get('Contents', [])
print(f"Found {len(files)} files to process")

for i, file in enumerate(files):
    key = file['Key']
    payload = {
        "Records": [{
            "s3": {
                "bucket": {"name": BUCKET},
                "object": {"key": key}
            }
        }]
    }
    lambda_client.invoke(
        FunctionName="IngestPHI",
        InvocationType="Event",
        Payload=json.dumps(payload)
    )
    print(f"Triggered {i+1}/{len(files)}: {key}")
    time.sleep(0.05)  # Small delay to avoid throttling

print("Done! Wait 5-10 minutes for Lambda to process all files")