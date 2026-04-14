import boto3
import random
import uuid
from decimal import Decimal
from faker import Faker
from datetime import datetime
from tqdm import tqdm

fake = Faker()

# AWS Clients
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
s3 = boto3.client('s3', region_name='us-east-1')
table = dynamodb.Table('PatientMetadata')

# Constants
icd10_codes = ['E11.9', 'I10', 'J18.9', 'K21.0', 'M79.3', 'Z87.891']
medications = ['Metformin', 'Lisinopril', 'Atorvastatin', 'Omeprazole', 'Amoxicillin']
BUCKET_NAME = 'simulated-attacker-bucket-sotonye1'

def generate_patient_record():
    dob = fake.date_of_birth(minimum_age=18, maximum_age=95)
    return {
        'patientId': str(uuid.uuid4()),
        'firstName': fake.first_name(),
        'lastName': fake.last_name(),
        'dob': str(dob),
        'mrn': fake.numerify('MRN-#######'),
        'diagnosis': random.choice(icd10_codes),
        'medication': random.choice(medications),
        'systolic': random.randint(90, 180),
        'diastolic': random.randint(60, 110),
        'glucoseLevel': Decimal(str(round(random.uniform(70, 300), 1))),  # Fixed: Convert to Decimal
        'visitDate': str(fake.date_between(start_date='-1y', end_date='today')),
        'providerId': fake.numerify('PROV-####'),
        'ingestedAt': datetime.now().isoformat() + 'Z',
        'sourceKey': 'direct_upload'
    }

print("=" * 50)
print("DFaaS-IF: Loading 1000 Patient Records")
print("=" * 50)

# Step 1: Write to DynamoDB
print("\n[1] Writing 1000 patient records to DynamoDB...")
for i in tqdm(range(1000), desc="DynamoDB writes"):
    record = generate_patient_record()
    table.put_item(Item=record)
print("1000 records added to DynamoDB")

# Step 2: Create stolen files in attacker bucket (Attack 2 evidence)
print("\n[2] Creating 1000 stolen files in attacker bucket...")
for i in tqdm(range(1000), desc="Stolen files"):
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=f'stolen/patient_{i}.json',
        Body='{"stolen":"patient_data","exfiltrated_at":"' + datetime.now().isoformat() + 'Z"}'
    )
print("1000 stolen files added to attacker bucket")

# Step 3: Verify counts
print("\n[3] Verification:")
dynamodb_count = table.scan(Select='COUNT')['Count']
print(f"   DynamoDB patient records: {dynamodb_count}")

stolen_count = len(s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix='stolen/').get('Contents', []))
print(f"   Stolen files in attacker bucket: {stolen_count}")

print("\n" + "=" * 50)
print("COMPLETE! Ready for framework evaluation.")
print("=" * 50)