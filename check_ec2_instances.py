import json
import boto3
from datetime import datetime, timezone, timedelta


client = boto3.client('ec2')
sns = boto3.client('sns')
cloudwatch = boto3.client('cloudwatch')
ec2 = boto3.resource('ec2')

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
        Period=60,
        Statistics=['Average'],
    )
    # print(response, "------Response----")
    # print((response['Datapoints']),"response",id)
    if len(response['Datapoints'])==0:
        return None
    else:
        return response['Datapoints'][0]['Average']
    

def running_instances():
    # create filter for instances in running state
    filters = [
        {
            'Name': 'instance-state-name',
            'Values': ['running']
        }
    ]

    # filter the instances based on filters() above
    instances = ec2.instances.filter(Filters=filters)

    # instantiate empty array
    RunningInstances = []

    for instance in instances:
        # for each instance, append to array and print instance id
        RunningInstances.append(instance.id)
    return len(RunningInstances)
def check_ec2_instance():
    print("hello")
    response = client.describe_instances()

    threshold_utilization = 5
    min_threshold_time = 80
    max_threshold_time = 240
    # print(response, "response---")
    if running_instances() > 0:
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instance_id = instance['InstanceId']
                print(f"Instance ID: {instance_id}")
                print(" ")
    
                current_time = datetime.now(timezone.utc).timestamp()
                creation_time = instance['LaunchTime'].timestamp()
    
                time_difference = current_time - creation_time
                print(f"Time Difference: {time_difference}")
                print(" ")
                try:
                    utilization_response = utilization(instance_id)
                    print("Utilization Response:", utilization_response)
                    print(" ")
                    average_utilization = utilization_response
                    if average_utilization!=None:
                        if average_utilization <= threshold_utilization:
                            if time_difference >= max_threshold_time:
                                sns_service(
                                    f"EC2 instance {instance_id} is underutilized and has crossed max threshold time. Terminating ec2 instance.")
                                terminate_ec2_instance(instance_id)
                            elif time_difference >= min_threshold_time and time_difference < max_threshold_time:
                                sns_service(
                                    "Please take necessary actions. This instance has exceeded minimum threshold time and is still underutilized.")
                            else:
                                pass
                    else:
                        pass
                except Exception as e:
                    print(f"Error processing instance {instance_id}: {e}")
                    print(" ")
    else:
        print(" ")
        print("No instances are present")
        sns_service("No instances are present")



def lambda_handler(event, context):
    check_ec2_instance()
