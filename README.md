# Serverless Forensic Frameworks Evaluation (DFaaS + IF-DSS)

**Student:** Sotonye Evelyn Charles | **Course:** GACS-7104

## Overview

This project evaluates two forensic frameworks (DFaaS and IF-DSS) in a simulated healthcare serverless environment on AWS.

## Files in This Repository

- `final.py` : Main Streamlit dashboard (3 pages)
- `direct_to_dynamodb.py` : Generates 1000 synthetic patient records directly to DynamoDB
- `lambda_ingest_phi.py` : IngestPHI Lambda function - processes patient data
- `lambda_attacker_exfil.py` : ExfiltratePHI Lambda function - simulates data theft (Attack 2)
- `delete_all_records.py` : Clears all DynamoDB records and S3 stolen files
- `batch_process.py` : Batch processing utility
- `generate_patient_data.py` : Alternative data generator using S3 triggers
- `backdoor.py` : Malicious Lambda code for Attack 3 (Lambda modification)
- `attack1_evidence.json` : Sample CloudTrail evidence from Attack 1
- `attack2_evidence.txt` : Sample EXFIL_COPY logs from Attack 2
- `generated_graphs/` : Folder containing 4 evaluation graphs (PNG files)

## AWS Setup Instructions

### Prerequisites
- AWS account (Free Tier works)
- AWS CLI installed and configured
- Python 3.13+

### Step 1: Create S3 Buckets (4 buckets)
- `aws s3 mb s3://phi-ingestion-bucket-YOURNAME --region us-east-1`
- `aws s3 mb s3://phi-processed-bucket-YOURNAME --region us-east-1`
- `aws s3 mb s3://forensic-evidence-bucket-YOURNAME --region us-east-1`
- `aws s3 mb s3://simulated-attacker-bucket-YOURNAME --region us-east-1`
- Enable versioning on all buckets
- Enable Object Lock on forensic bucket (compliance mode)

### Step 2: Create DynamoDB Table
- Table name: `PatientMetadata`
- Partition key: `patientId` (String)
- Billing mode: PAY_PER_REQUEST
- Enable DynamoDB Streams (NEW_AND_OLD_IMAGES)
- Enable Point-in-time recovery

### Step 3: Create IAM Roles for Lambda
- Role name: `LambdaIngestRole`
- Permissions: DynamoDB write, S3 read/write, CloudWatch logs
- Role name: `LambdaAttackerRole`
- Permissions: S3 list/read/write (attacker bucket only)

### Step 4: Deploy Lambda Functions
- `IngestPHI` : Uses `lambda_ingest_phi.py`
- `ExfiltratePHI` : Uses `lambda_attacker_exfil.py`
- Memory: 1024 MB
- Timeout: 300 seconds
- Add S3 trigger to IngestPHI (bucket: phi-ingestion-bucket-YOURNAME, event: PUT)

### Step 5: Create CloudTrail Trail
- Trail name: `healthcare-forensic-trail`
- S3 bucket: `forensic-evidence-bucket-YOURNAME`
- Enable log file validation (SHA-256)
- Enable multi-region trail
- Start logging

### Step 6: Configure AWS CLI
- `aws configure`
- Enter Access Key ID
- Enter Secret Access Key
- Default region: `us-east-1`
- Output format: `json`

### Security Note
> **IMPORTANT:** Replace `YOURNAME` with your unique identifier  in all bucket names and ARNs to avoid naming conflicts. All bucket names use `sotonye1` as a suffix. **You must replace `sotonye1` with your own unique identifier
## How to Run

- Install dependencies: `pip install streamlit boto3 pandas matplotlib faker tqdm`
- Generate 1000 records: `python direct_to_dynamodb.py`
- Run dashboard: `streamlit run final.py`
- Execute attacks in "Attack and Evidence" page
