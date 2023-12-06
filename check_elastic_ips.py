import json
import boto3
from botocore.exceptions import ClientError
ec2 = boto3.client('ec2')
def release_elastic_ips(id):
    ec2 = boto3.client('ec2')
    try:
        response = ec2.release_address(AllocationId=id)
    except ClientError as e:
        print(e)
def lambda_handler(event, context):
    
    
    response = ec2.describe_addresses()
    print(response)
    print(" ")
    print(" ")
    print(" ")
    if len(response['Addresses'])!=0:
        id = response['Addresses'][0]['AllocationId']
        if 'AssociationId' not in response['Addresses']:
            print(f"Elatic IP {id} is released")
            release_elastic_ips(id)
        else:
            pass
    else:
        print("No elastic IPs present")
