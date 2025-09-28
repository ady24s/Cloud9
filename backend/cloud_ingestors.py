# app/cloud_ingestors.py
from sqlalchemy.orm import Session
from backend.models import CloudCredential, CloudMetric
from backend.crypto_utils import decrypt_text  # FIXED import
import json, datetime

# ---------- AWS ----------
def ingest_aws(db: Session, user_id: int):
    try:
        import boto3
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

    ec2 = boto3.client("ec2", aws_access_key_id=access, aws_secret_access_key=secret)
    cw = boto3.client("cloudwatch", aws_access_key_id=access, aws_secret_access_key=secret)

    # list instances
    instances = []
    try:
        resp = ec2.describe_instances()
        for r in resp.get("Reservations", []):
            for i in r.get("Instances", []):
                instances.append(i["InstanceId"])
    except Exception as e:
        print(f"[AWS] EC2 describe failed: {e}")
        return 0

    end = datetime.datetime.utcnow()
    start = end - datetime.timedelta(minutes=10)
    rows = 0

    for iid in instances[:20]:  # limit to first 20
        cpu = _aws_get_avg(cw, "AWS/EC2", "CPUUtilization", "InstanceId", iid, start, end, "Percent")
        net_in = _aws_get_sum(cw, "AWS/EC2", "NetworkIn", "InstanceId", iid, start, end, "Bytes")
        net_out = _aws_get_sum(cw, "AWS/EC2", "NetworkOut", "InstanceId", iid, start, end, "Bytes")

        m = CloudMetric(
            provider="aws",
            vm_id=iid,
            timestamp=end.isoformat() + "Z",
            cpu_usage=cpu or 0.0,
            memory_usage=0.0,  # requires CloudWatch Agent, leave 0 if not available
            network_traffic=float((net_in or 0) + (net_out or 0)),
            power_consumption=0.0,
            execution_time=0.0,
            task_type="ec2",
            user_id=user_id,
        )
        db.add(m)
        rows += 1
    db.commit()
    return rows


def _aws_get_avg(cw, ns, metric, dim_name, dim_value, start, end, unit):
    try:
        r = cw.get_metric_statistics(
            Namespace=ns,
            MetricName=metric,
            Dimensions=[{"Name": dim_name, "Value": dim_value}],
            StartTime=start, EndTime=end, Period=300,
            Statistics=["Average"], Unit=unit,
        )
        dp = r.get("Datapoints", [])
        if dp:
            dp.sort(key=lambda x: x["Timestamp"])
            return float(dp[-1].get("Average", 0.0))
    except:
        return None
    return None


def _aws_get_sum(cw, ns, metric, dim_name, dim_value, start, end, unit):
    try:
        r = cw.get_metric_statistics(
            Namespace=ns,
            MetricName=metric,
            Dimensions=[{"Name": dim_name, "Value": dim_value}],
            StartTime=start, EndTime=end, Period=300,
            Statistics=["Sum"], Unit=unit,
        )
        dp = r.get("Datapoints", [])
        if dp:
            dp.sort(key=lambda x: x["Timestamp"])
            return float(dp[-1].get("Sum", 0.0))
    except:
        return None
    return None


# ---------- GCP ----------
def ingest_gcp(db: Session, user_id: int):
    try:
        from google.cloud import monitoring_v3
        from google.oauth2 import service_account
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

    sa_json = decrypt_text(cred.extra_json_enc)
    info = json.loads(sa_json)
    project_id = info.get("project_id")
    if not project_id:
        return 0

    creds = service_account.Credentials.from_service_account_info(info)
    client = monitoring_v3.MetricServiceClient(credentials=creds)

    end = datetime.datetime.utcnow()
    start = end - datetime.timedelta(minutes=10)
    interval = monitoring_v3.TimeInterval(
        end_time={"seconds": int(end.timestamp())},
        start_time={"seconds": int(start.timestamp())},
    )

    metric_type = "compute.googleapis.com/instance/cpu/utilization"
    results = client.list_time_series(
        request={
            "name": f"projects/{project_id}",
            "filter": f'metric.type = "{metric_type}"',
            "interval": interval,
            "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
        }
    )

    rows = 0
    for ts in results:
        vm_id = ts.resource.labels.get("instance_id", "unknown")
        if not ts.points:
            continue
        value = float(ts.points[0].value.double_value) * 100.0
        m = CloudMetric(
            provider="gcp",
            vm_id=vm_id,
            timestamp=end.isoformat() + "Z",
            cpu_usage=value,
            memory_usage=0.0,
            network_traffic=0.0,
            power_consumption=0.0,
            execution_time=0.0,
            task_type="gce",
            user_id=user_id,
        )
        db.add(m)
        rows += 1
    db.commit()
    return rows


# ---------- Azure ----------
def ingest_azure(db: Session, user_id: int):
    try:
        from azure.identity import ClientSecretCredential
        from azure.mgmt.monitor import MonitorManagementClient
        from azure.mgmt.compute import ComputeManagementClient
    except ImportError:
        print("[ingest] azure-identity/azure-mgmt-monitor not installed, skipping Azure")
        return 0

    cred = (
        db.query(CloudCredential)
        .filter(CloudCredential.user_id == user_id, CloudCredential.provider == "azure")
        .first()
    )
    if not cred or not cred.extra_json_enc:
        return 0

    info = json.loads(decrypt_text(cred.extra_json_enc) or "{}")
    tenant_id = info.get("tenant_id")
    client_id = info.get("client_id")
    client_secret = info.get("client_secret")
    subscription_id = info.get("subscription_id")
    resource_group = info.get("resource_group")

    if not all([tenant_id, client_id, client_secret, subscription_id]):
        return 0

    credential = ClientSecretCredential(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret)
    compute_client = ComputeManagementClient(credential, subscription_id)
    monitor_client = MonitorManagementClient(credential, subscription_id)

    # List all VMs in the subscription (or optionally filter by resource_group)
    vms = compute_client.virtual_machines.list_all()
    end = datetime.datetime.utcnow()
    start = end - datetime.timedelta(minutes=10)
    rows = 0

    for vm in vms:
        vm_id = vm.id
        try:
            metrics_data = monitor_client.metrics.list(
                resource_uri=vm_id,
                timespan=f"{start.isoformat()}Z/{end.isoformat()}Z",
                interval="PT5M",
                metricnames="Percentage CPU",
                aggregation="Average",
            )
            for item in metrics_data.value:
                if not item.timeseries:
                    continue
                data_points = item.timeseries[0].data
                if not data_points:
                    continue
                avg = data_points[-1].average or 0.0
                m = CloudMetric(
                    provider="azure",
                    vm_id=vm.name,
                    timestamp=end.isoformat() + "Z",
                    cpu_usage=avg,
                    memory_usage=0.0,
                    network_traffic=0.0,
                    power_consumption=0.0,
                    execution_time=0.0,
                    task_type="vm",
                    user_id=user_id,
                )
                db.add(m)
                rows += 1
        except Exception as e:
            print(f"[Azure] Failed metrics for VM {vm_id}: {e}")
            continue
    db.commit()
    return rows
