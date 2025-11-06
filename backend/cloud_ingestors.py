# backend/cloud_ingestors.py
from sqlalchemy.orm import Session
from backend.models import CloudCredential, CloudMetric
import json, datetime
from backend.crypto_utils import decrypt_text


# ---------- AWS ----------
def ingest_aws(db: Session, user_id: int):
    try:
        import boto3
        from botocore.exceptions import ClientError
    except ImportError:
        print("[ingest] boto3 not installed, skipping AWS")
        return 0

    cred = (
        db.query(CloudCredential)
        .filter(CloudCredential.user_id == user_id, CloudCredential.provider == "aws")
        .first()
    )
    if not cred or not cred.access_key_enc or not cred.secret_key_enc:
        return 0

    access = decrypt_text(cred.access_key_enc)
    secret = decrypt_text(cred.secret_key_enc)

    try:
        # Initialize AWS clients
        session = boto3.Session(
            aws_access_key_id=access,
            aws_secret_access_key=secret,
            region_name='us-east-1'  # Default region
        )
        
        ec2 = session.client('ec2')
        cloudwatch = session.client('cloudwatch')
        s3 = session.client('s3')
        
        end = datetime.datetime.utcnow()
        start = end - datetime.timedelta(hours=1)
        rows = 0

        # Get all running instances across all regions
        regions = [region['RegionName'] for region in ec2.describe_regions()['Regions']]
        
        for region in regions[:3]:  # Limit to 3 regions for performance
            try:
                regional_ec2 = boto3.client(
                    'ec2',
                    aws_access_key_id=access,
                    aws_secret_access_key=secret,
                    region_name=region
                )
                
                # Get running instances
                response = regional_ec2.describe_instances(
                    Filters=[{'Name': 'instance-state-name', 'Values': ['running', 'stopped']}]
                )
                
                for reservation in response.get('Reservations', []):
                    for instance in reservation.get('Instances', []):
                        instance_id = instance['InstanceId']
                        instance_type = instance.get('InstanceType', 'unknown')
                        state = instance['State']['Name']
                        
                        # Get CPU utilization from CloudWatch
                        cpu_usage = _aws_get_metric_average(
                            cloudwatch, region, 'AWS/EC2', 'CPUUtilization',
                            'InstanceId', instance_id, start, end
                        ) or 0.0
                        
                        # Get network metrics
                        network_in = _aws_get_metric_sum(
                            cloudwatch, region, 'AWS/EC2', 'NetworkIn',
                            'InstanceId', instance_id, start, end
                        ) or 0.0
                        
                        network_out = _aws_get_metric_sum(
                            cloudwatch, region, 'AWS/EC2', 'NetworkOut', 
                            'InstanceId', instance_id, start, end
                        ) or 0.0

                        # Create metric record
                        metric = CloudMetric(
                            provider="aws",
                            vm_id=instance_id,
                            vm_name=instance_id,  # AWS doesn't have friendly names by default
                            timestamp=end.isoformat() + "Z",
                            cpu_usage=cpu_usage,
                            memory_usage=0.0,  # Requires CloudWatch agent
                            network_traffic=float(network_in + network_out),
                            power_consumption=0.0,
                            execution_time=0.0,
                            task_type=instance_type,
                            region=region,
                            instance_state=state,
                            user_id=user_id,
                        )
                        db.add(metric)
                        rows += 1
                        
            except ClientError as e:
                print(f"[AWS] Error in region {region}: {e}")
                continue

        db.commit()
        print(f"[AWS] Ingested {rows} instance metrics for user {user_id}")
        return rows
        
    except Exception as e:
        print(f"[AWS] General error: {e}")
        db.rollback()
        return 0


def _aws_get_metric_average(cw, region, namespace, metric_name, dimension_name, dimension_value, start, end):
    try:
        response = cw.get_metric_statistics(
            Namespace=namespace,
            MetricName=metric_name,
            Dimensions=[{'Name': dimension_name, 'Value': dimension_value}],
            StartTime=start,
            EndTime=end,
            Period=300,
            Statistics=['Average'],
            Unit='Percent'
        )
        datapoints = response.get('Datapoints', [])
        if datapoints:
            # Get the most recent datapoint
            datapoints.sort(key=lambda x: x['Timestamp'])
            return float(datapoints[-1]['Average'])
    except Exception as e:
        print(f"[AWS] Metric error for {metric_name}: {e}")
    return None


def _aws_get_metric_sum(cw, region, namespace, metric_name, dimension_name, dimension_value, start, end):
    try:
        response = cw.get_metric_statistics(
            Namespace=namespace,
            MetricName=metric_name,
            Dimensions=[{'Name': dimension_name, 'Value': dimension_value}],
            StartTime=start,
            EndTime=end,
            Period=300,
            Statistics=['Sum'],
            Unit='Bytes'
        )
        datapoints = response.get('Datapoints', [])
        if datapoints:
            datapoints.sort(key=lambda x: x['Timestamp'])
            return float(datapoints[-1]['Sum'])
    except Exception as e:
        print(f"[AWS] Metric error for {metric_name}: {e}")
    return None


# ---------- GCP ----------
def ingest_gcp(db: Session, user_id: int):
    try:
        from google.cloud import monitoring_v3, compute_v1
        from google.oauth2 import service_account
        from google.api_core.exceptions import GoogleAPIError
    except ImportError:
        print("[ingest] google-cloud-monitoring not installed, skipping GCP")
        return 0

    cred = (
        db.query(CloudCredential)
        .filter(CloudCredential.user_id == user_id, CloudCredential.provider == "gcp")
        .first()
    )
    if not cred or not cred.extra_json_enc:
        return 0

    try:
        sa_json = decrypt_text(cred.extra_json_enc)
        info = json.loads(sa_json)
        project_id = info.get("project_id")
        if not project_id:
            return 0

        credentials = service_account.Credentials.from_service_account_info(info)
        
        # Initialize clients
        monitoring_client = monitoring_v3.MetricServiceClient(credentials=credentials)
        compute_client = compute_v1.InstancesClient(credentials=credentials)
        
        end = datetime.datetime.utcnow()
        start = end - datetime.timedelta(hours=1)
        rows = 0

        # Get all zones and instances
        zones_client = compute_v1.ZonesClient(credentials=credentials)
        zones = [zone.name for zone in zones_client.list(project=project_id)]
        
        for zone in zones[:3]:  # Limit to 3 zones for performance
            try:
                # List instances in this zone
                instances = compute_client.list(project=project_id, zone=zone)
                
                for instance in instances:
                    instance_id = str(instance.id)
                    instance_name = instance.name
                    machine_type = instance.machine_type.split('/')[-1]
                    status = instance.status.lower()
                    
                    # Get CPU utilization
                    cpu_usage = _gcp_get_metric(
                        monitoring_client, project_id,
                        'compute.googleapis.com/instance/cpu/utilization',
                        instance_id, start, end
                    ) or 0.0
                    
                    # Get network traffic
                    network_usage = _gcp_get_metric(
                        monitoring_client, project_id,
                        'compute.googleapis.com/instance/network/received_bytes_count', 
                        instance_id, start, end
                    ) or 0.0

                    metric = CloudMetric(
                        provider="gcp",
                        vm_id=instance_id,
                        vm_name=instance_name,
                        timestamp=end.isoformat() + "Z",
                        cpu_usage=cpu_usage * 100,  # Convert to percentage
                        memory_usage=0.0,
                        network_traffic=float(network_usage),
                        power_consumption=0.0,
                        execution_time=0.0,
                        task_type=machine_type,
                        region=zone,
                        instance_state=status,
                        user_id=user_id,
                    )
                    db.add(metric)
                    rows += 1
                    
            except GoogleAPIError as e:
                print(f"[GCP] Error in zone {zone}: {e}")
                continue

        db.commit()
        print(f"[GCP] Ingested {rows} instance metrics for user {user_id}")
        return rows
        
    except Exception as e:
        print(f"[GCP] General error: {e}")
        db.rollback()
        return 0


def _gcp_get_metric(client, project_id, metric_type, instance_id, start, end):
    try:
        interval = monitoring_v3.TimeInterval({
            "end_time": {"seconds": int(end.timestamp())},
            "start_time": {"seconds": int(start.timestamp())},
        })
        
        results = client.list_time_series(
            request={
                "name": f"projects/{project_id}",
                "filter": f'metric.type = "{metric_type}" AND metric.labels.instance_id = "{instance_id}"',
                "interval": interval,
                "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
            }
        )
        
        for series in results:
            if series.points:
                # Get the most recent point
                return float(series.points[0].value.double_value)
                
    except Exception as e:
        print(f"[GCP] Metric error for {metric_type}: {e}")
    return None


# ---------- Azure ----------
def ingest_azure(db: Session, user_id: int):
    try:
        from azure.identity import ClientSecretCredential
        from azure.mgmt.compute import ComputeManagementClient
        from azure.mgmt.monitor import MonitorManagementClient
        from azure.mgmt.subscription import SubscriptionClient
        from azure.core.exceptions import ResourceNotFoundError
    except ImportError:
        print("[ingest] azure-mgmt packages not installed, skipping Azure")
        return 0

    cred = (
        db.query(CloudCredential)
        .filter(CloudCredential.user_id == user_id, CloudCredential.provider == "azure")
        .first()
    )
    if not cred or not cred.extra_json_enc:
        return 0

    try:
        info = json.loads(decrypt_text(cred.extra_json_enc) or "{}")
        tenant_id = info.get("tenant_id")
        client_id = info.get("client_id") 
        client_secret = info.get("client_secret")
        subscription_id = info.get("subscription_id")

        if not all([tenant_id, client_id, client_secret, subscription_id]):
            return 0

        credential = ClientSecretCredential(
            tenant_id=tenant_id, 
            client_id=client_id, 
            client_secret=client_secret
        )
        
        # Initialize clients
        compute_client = ComputeManagementClient(credential, subscription_id)
        monitor_client = MonitorManagementClient(credential, subscription_id)
        
        end = datetime.datetime.utcnow()
        start = end - datetime.timedelta(hours=1)
        rows = 0

        # Get all virtual machines
        vms = compute_client.virtual_machines.list_all()
        
        for vm in vms:
            try:
                vm_name = vm.name
                vm_id = vm.id
                location = vm.location
                vm_size = vm.hardware_profile.vm_size if vm.hardware_profile else "unknown"
                
                # Get power state
                power_state = "unknown"
                instance_view = compute_client.virtual_machines.instance_view(
                    resource_group_name=vm.id.split('/')[4],  # Extract resource group
                    vm_name=vm_name
                )
                for status in instance_view.statuses:
                    if status.code.startswith('PowerState/'):
                        power_state = status.code.split('/')[-1]
                        break
                
                # Get CPU metrics
                cpu_usage = _azure_get_metric(
                    monitor_client, vm_id, 'Percentage CPU', start, end
                ) or 0.0

                metric = CloudMetric(
                    provider="azure",
                    vm_id=vm_id,
                    vm_name=vm_name,
                    timestamp=end.isoformat() + "Z",
                    cpu_usage=cpu_usage,
                    memory_usage=0.0,  # Azure doesn't provide memory by default
                    network_traffic=0.0,
                    power_consumption=0.0,
                    execution_time=0.0,
                    task_type=vm_size,
                    region=location,
                    instance_state=power_state,
                    user_id=user_id,
                )
                db.add(metric)
                rows += 1
                
            except (ResourceNotFoundError, Exception) as e:
                print(f"[Azure] Error processing VM {vm.name}: {e}")
                continue

        db.commit()
        print(f"[Azure] Ingested {rows} VM metrics for user {user_id}")
        return rows
        
    except Exception as e:
        print(f"[Azure] General error: {e}")
        db.rollback()
        return 0


def _azure_get_metric(monitor_client, resource_uri, metric_name, start, end):
    try:
        metrics_data = monitor_client.metrics.list(
            resource_uri=resource_uri,
            timespan=f"{start.isoformat()}Z/{end.isoformat()}Z",
            interval="PT1H",
            metricnames=metric_name,
            aggregation="Average"
        )
        
        for item in metrics_data.value:
            if item.timeseries:
                for data in item.timeseries[0].data:
                    if data.average is not None:
                        return float(data.average)
    except Exception as e:
        print(f"[Azure] Metric error for {metric_name}: {e}")
    return None