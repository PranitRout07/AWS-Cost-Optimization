import json
import boto3
from datetime import datetime,timezone,timedelta


client = boto3.client('ec2')
sns = boto3.client('sns')
cloudwatch = boto3.client('cloudwatch')

def sns_service(message):
   topic_arn = ''
   sns.publish(
     TopicArn=topic_arn,
     Message=message
        )

def terminate_ec2_instance(id):
    
    
	response = client.terminate_instances(
    		InstanceIds=[
        		id,
    			]
		)
	print("hhhhh")

def utilization(id):
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=1)
    response = cloudwatch.get_metric_statistics(
        Namespace='AWS/EC2',
        MetricName='CPUUtilization',
        Dimensions=[
            {
                'Name': 'InstanceId',
                'Value': id
            },
        ],
    StartTime=start_time,
    EndTime=end_time,
    Period = 60,
    Statistics = ['Average'],
    )
    print(response,"------Response----")
    return response


def check_ec2_instance():
    print("hello")
    response = client.describe_instances()

    threshold_utilization = 5
    min_threshold_time = 40
    max_threshold_time = 120
    print(response,"response---")
    if len(response['Reservations'])>0 and response['Reservations'][0]['Instances'][0]['State']['Name']!='terminated' and response['Reservations'][0]['Instances'][0]['State']['Name']!='stopped':
        for reservation in response['Reservations']:
            
                for instance in reservation['Instances']:
                    instance_id = instance['InstanceId']
                    print(f"Instance ID: {instance_id}")
    
                    current_time = (datetime.now(timezone.utc)).timestamp()
                    creation_time = (instance['LaunchTime']).timestamp()
    
                    time_difference = (current_time - creation_time)
                    print(time_difference)
                    print(utilization(instance_id),"-----utilization response")
                    print("utilization(instance_id)['Datapoints'][0]['Average']----",utilization(instance_id)['Datapoints'][0]['Average'])
                    if utilization(instance_id)['Datapoints'][0]['Average'] <= threshold_utilization :
                        if time_difference >= max_threshold_time:
                            sns_service(f"EC2 instance is under utilized and has crossed max threshold time . So terminating ec2 instance {instance_id}")
    
                            terminate_ec2_instance(instance_id)
                        elif time_difference >= min_threshold_time and time_difference < max_threshold_time:
    
                            sns_service("Please take neccessary actions . This instance has exceeded minimum threshold time and still it is under utilized")
                        else:
                            pass
    else:
        print("No instances are present")
        sns_service("No instances are present")


def lambda_handler(event, context):
    check_ec2_instance()
