import json
import boto3
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamo = boto3.resource('dynamodb')
s3 = boto3.client('s3')
table = dynamo.Table(os.environ['DYNAMODB_TABLE'])
OUT_BUCKET = os.environ['OUTPUT_BUCKET']

REQUIRED_FIELDS = ['patientId', 'firstName', 'lastName', 'dob', 'mrn', 'diagnosis', 'medication', 'visitDate']

def lambda_handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        logger.info(f'Processing s3://{bucket}/{key}')
        
        # Download the record
        obj = s3.get_object(Bucket=bucket, Key=key)
        data = json.loads(obj['Body'].read().decode('utf-8'))
        
        # Validate required fields
        missing = [f for f in REQUIRED_FIELDS if f not in data]
        if missing:
            logger.error(f'VALIDATION_FAIL patientId={data.get("patientId","unknown")} missing={missing}')
            raise ValueError(f'Missing fields: {missing}')
        
        # Write to DynamoDB
        table.put_item(Item={
            'patientId': data['patientId'],
            'mrn': data['mrn'],
            'lastName': data['lastName'],
            'firstName': data['firstName'],
            'dob': data['dob'],
            'diagnosis': data['diagnosis'],
            'medication': data['medication'],
            'visitDate': data['visitDate'],
            'ingestedAt': data['timestamp'],
            'sourceKey': key
        })
        logger.info(f'DYNAMO_WRITE patientId={data["patientId"]} mrn={data["mrn"]}')
        
        # Copy to processed bucket
        s3.copy_object(
            Bucket=OUT_BUCKET,
            CopySource={'Bucket': bucket, 'Key': key},
            Key=key.replace('incoming/', 'processed/')
        )
        logger.info(f'COPY_SUCCESS destination={OUT_BUCKET}')
    
    return {'statusCode': 200, 'body': 'OK'}