import boto3
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def fetch_ec2_instances():
    ec2 = boto3.client('ec2', region_name=os.getenv("AWS_REGION", "us-east-1"))
    try:
        response = ec2.describe_instances()
        print("EC2 Response:", response)  # Debugging
        instances = []
        for reservation in response.get('Reservations', []):
            for instance in reservation.get('Instances', []):
                instances.append({
                    'id': instance['InstanceId'],
                    'type': instance['InstanceType'],
                    'state': instance['State']['Name'],
                    'launch_time': instance['LaunchTime'].strftime("%Y-%m-%d %H:%M:%S"),
                })
        return instances
    except Exception as e:
        print("Error fetching EC2 instances:", e)  # Debugging
        raise



def fetch_s3_buckets():
    s3 = boto3.client('s3', region_name=os.getenv("AWS_REGION", "us-east-1"))
    response = s3.list_buckets()
    buckets = [
        {
            "name": bucket["Name"],
            "creation_date": bucket["CreationDate"].strftime("%Y-%m-%d %H:%M:%S"),
        }
        for bucket in response.get("Buckets", [])
    ]
    return buckets

def find_idle_instances(instances):
    try:
        print("Instances Passed to Idle Check:", instances)  # Debugging
        idle_instances = [instance for instance in instances if instance.get('state') == 'stopped']
        print("Idle Instances Found:", idle_instances)  # Debugging
        return idle_instances
    except Exception as e:
        print("Error in find_idle_instances:", e)  # Debugging
        raise


