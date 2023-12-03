import json
import boto3
from datetime import datetime, timezone

client = boto3.client('ec2')


def sns_service(message):
    topic_arn = ' ' #SNS Topic ARN
    client.publish(
        TopicArn=topic_arn,
        Message=message
    )


def delete_vol(id):
    print("Deleting volume id", id)
    response = client.delete_volume(
        VolumeId=id,
    )


def lambda_handler(event, context):
    # check for unused volume
    check_volume()


def check_volume():
    min_threshold_time = 30  # in seconds
    max_threshold_time = 90  # in seconds

    response = client.describe_volumes()

    # print(response)
    if len(response['Volumes']) == 0:
        print("No volume is present")
    else:
        volumes = response['Volumes']
        current_time = datetime.now(timezone.utc)

        for volume in volumes:
            creation_time = volume['CreateTime']
            time_difference = (current_time - creation_time).total_seconds()

            # print(time_difference,"seconds for volume id : ",volume['VolumeId'])
            if volume['State'] == 'available':
                if time_difference >= max_threshold_time:
                    print("This volume has exceeded maximum threshold time")

                    sns_service(f"This volume has exceeded maximum threshold time.Deleting volume {volume['VolumeId']}")
                    delete_vol(volume['VolumeId'])

                elif time_difference >= min_threshold_time and time_difference < max_threshold_time:

                    print("Please take neccessary actions . This volume has exceeded minimum threshold time")
                    sns_service("Please take neccessary actions . This volume has exceeded minimum threshold time")
                else:
                    pass
            else:
                pass

