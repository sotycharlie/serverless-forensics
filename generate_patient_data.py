# generate_patient_data.py - Updated for 1000 records
import json
import random
import uuid
import boto3
import sys
from faker import Faker
from datetime import datetime
from tqdm import tqdm

# Update these values for your setup
BUCKET = "phi-ingestion-bucket-sotonye1"  # Your raw ingestion bucket
REGION = "us-east-1"
NUM_RECORDS = 1000  # CHANGE THIS TO 1000

def upload_records(count=NUM_RECORDS):
    fake = Faker()
    s3 = boto3.client('s3', region_name=REGION)
    dynamodb = boto3.resource('dynamodb', region_name=REGION)
    table = dynamodb.Table('PatientMetadata')
    
    icd10_codes = ['E11.9', 'I10', 'J18.9', 'K21.0', 'M79.3', 'Z87.891']
    medications = ['Metformin', 'Lisinopril', 'Atorvastatin', 'Omeprazole', 'Amoxicillin']
    
    print(f"Generating {count} synthetic patient records...")
    print(f"Bucket: {BUCKET}")
    print(f"DynamoDB Table: PatientMetadata")
    
    success_count = 0
    
    for i in tqdm(range(count), desc="Uploading records"):
        dob = fake.date_of_birth(minimum_age=18, maximum_age=95)
        
        # Create patient record
        patient_id = str(uuid.uuid4())
        record = {
            'patientId': patient_id,
            'firstName': fake.first_name(),
            'lastName': fake.last_name(),
            'dob': str(dob),
            'mrn': fake.numerify('MRN-#######'),
            'diagnosis': random.choice(icd10_codes),
            'medication': random.choice(medications),
            'systolic': random.randint(90, 180),
            'diastolic': random.randint(60, 110),
            'glucoseLevel': round(random.uniform(70, 300), 1),
            'visitDate': str(fake.date_between(start_date='-1y', end_date='today')),
            'providerId': fake.numerify('PROV-####'),
            'timestamp': datetime.now().isoformat() + 'Z'
        }
        
        # Upload to S3 (triggers Lambda)
        key = f"incoming/{patient_id}.json"
        try:
            s3.put_object(
                Bucket=BUCKET,
                Key=key,
                Body=json.dumps(record),
                ContentType='application/json'
            )
            success_count += 1
        except Exception as e:
            print(f"Error uploading {key}: {e}")
    
    print(f"Done! {success_count} of {count} records uploaded to S3.")
    print(f"Lambda IngestPHI should automatically process them to DynamoDB.")
    
    # Wait a moment and check DynamoDB count
    print("\nWaiting 5 seconds for Lambda to process...")
    import time
    time.sleep(5)
    
    response = table.scan(Select='COUNT')
    dynamodb_count = response.get('Count', 0)
    print(f"DynamoDB record count: {dynamodb_count}")

if __name__ == '__main__':
    # Allow command line override: python generate_patient_data.py 1000
    count = int(sys.argv[1]) if len(sys.argv) > 1 else NUM_RECORDS
    upload_records(count)