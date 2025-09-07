#!/usr/bin/env python3
"""
Change EC2 instance type based on schedule.

Usage:
  ec2_type_switcher.py --instance-id=<id> --csv=<path> --region=<region> [--default-type=<type>] [--profile=<profile>] [--dry-run]

Options:
  --instance-id=<id>      EC2 instance ID (e.g., i-0123456789abcdef0)
  --csv=<path>            Path to schedule CSV file [default: ec2_schedule.csv]
  --region=<region>       AWS region (e.g., us-east-1) [default: us-east-1]
  --default-type=<type>   Default instance type [default: t2.micro]
  --profile=<profile>     AWS CLI profile to use
  --dry-run               Simulate changes without applying them
"""

import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
from docopt import docopt
import boto3
from botocore.exceptions import ClientError

FAMILY_ARCH = {
    "t2": "x86_64",
    "t3": "x86_64",
    "t3a": "x86_64",
    "t4g": "arm64",
}

def family_of(inst_type: str) -> str:
    return inst_type.split(".")[0]

def arch_for_family(fam: str) -> str | None:
    return FAMILY_ARCH.get(fam)

def now_in_monterrrey():
    return datetime.now(ZoneInfo("America/Monterrey"))

def load_schedule(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)

    required_cols = {"Day", "Start", "End", "EC2_Type"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"CSV must include these columns: {required_cols}")

    # Parse time columns
    df["Start"] = pd.to_datetime(df["Start"], format="%H:%M").dt.time
    df["End"] = pd.to_datetime(df["End"], format="%H:%M").dt.time
    df["Day"] = df["Day"].astype(int)
    df["EC2_Type"] = df["EC2_Type"].astype(str).str.strip()

    return df

def desired_type_for_now(df: pd.DataFrame, default_type: str, now_dt: datetime) -> str:
    today = now_dt.day
    now_t = now_dt.time()
    matches = df[df["Day"] == today]
    for _, row in matches.iterrows():
        if row["Start"] <= now_t <= row["End"]:
            return row["EC2_Type"]
    return default_type

def get_instance_description(ec2, instance_id: str):
    resp = ec2.describe_instances(InstanceIds=[instance_id])
    return resp["Reservations"][0]["Instances"][0]

def get_image_architecture(ec2, image_id: str) -> str | None:
    try:
        img = ec2.describe_images(ImageIds=[image_id])["Images"][0]
        return img.get("Architecture")
    except Exception:
        return None

def is_in_asg(instance_desc: dict) -> bool:
    tags = instance_desc.get("Tags", [])
    return any(t.get("Key") == "aws:autoscaling:groupName" for t in tags)

def ensure_compatible(target_type: str, instance_desc: dict, ec2):
    fam = family_of(target_type)
    target_arch = arch_for_family(fam)
    if not target_arch:
        return (False, f"Unknown architecture for family '{fam}'. Please check manually.")
    image_id = instance_desc.get("ImageId")
    ami_arch = get_image_architecture(ec2, image_id) if image_id else None
    if ami_arch and ami_arch != target_arch:
        return (False, f"Incompatible: AMI ({ami_arch}) vs destination {target_type} ({target_arch}).")
    return (True, "OK")

def stop_modify_start(ec2, instance_id: str, current_type: str, new_type: str, dry_run: bool):
    desc = get_instance_description(ec2, instance_id)
    state = desc["State"]["Name"]

    if state not in ("stopped", "stopping"):
        print(f"[INFO] Stopping instance {instance_id} (state: {state})...")
        try:
            ec2.stop_instances(InstanceIds=[instance_id], DryRun=dry_run)
        except ClientError as e:
            if e.response["Error"].get("Code") == "DryRunOperation":
                print("[DRY-RUN] stop_instances OK (simulated).")
            else:
                raise
        if not dry_run:
            waiter = ec2.get_waiter("instance_stopped")
            waiter.wait(InstanceIds=[instance_id])
            print("[INFO] Instance stopped.")
    else:
        print(f"[INFO] Instance already stopping/stopped: {state}")

    print(f"[INFO] Changing instance type from {current_type} to {new_type}...")
    try:
        ec2.modify_instance_attribute(
            InstanceId=instance_id,
            InstanceType={"Value": new_type},
            DryRun=dry_run,
        )
    except ClientError as e:
        if e.response["Error"].get("Code") == "DryRunOperation":
            print("[DRY-RUN] modify_instance_attribute OK (simulated).")
        else:
            raise

    print(f"[INFO] Starting instance {instance_id}...")
    try:
        ec2.start_instances(InstanceIds=[instance_id], DryRun=dry_run)
    except ClientError as e:
        if e.response["Error"].get("Code") == "DryRunOperation":
            print("[DRY-RUN] start_instances OK (simulated).")
        else:
            raise
    if not dry_run:
        waiter = ec2.get_waiter("instance_running")
        waiter.wait(InstanceIds=[instance_id])
        print("[INFO] Instance is now running.")

def main():
    args = docopt(__doc__)

    instance_id = args["--instance-id"]
    csv_path = args["--csv"]
    region = args["--region"]
    default_type = args["--default-type"]
    profile = args["--profile"]
    dry_run = args["--dry-run"]

    if profile:
        boto3.setup_default_session(profile_name=profile, region_name=region)
    ec2 = boto3.client("ec2", region_name=region)

    schedule_df = load_schedule(csv_path)
    now = now_in_monterrrey()
    desired_type = desired_type_for_now(schedule_df, default_type, now)

    inst = get_instance_description(ec2, instance_id)
    current_type = inst["InstanceType"]

    print(f"[INFO] Current time: {now.isoformat()} (America/Monterrey)")
    print(f"[INFO] Current type: {current_type} | Desired type: {desired_type}")

    if desired_type == current_type:
        print("[INFO] No change required.")
        return

    if is_in_asg(inst):
        raise SystemExit("The instance belongs to an Auto Scaling Group; modify the Launch Template/Configuration instead.")

    ok, msg = ensure_compatible(desired_type, inst, ec2)
    if not ok:
        raise SystemExit(f"Compatibility check failed: {msg}")
    else:
        print(f"[INFO] Compatibility: {msg}")

    stop_modify_start(ec2, instance_id, current_type, desired_type, dry_run)
    print("[DONE] Change applied.")

if __name__ == "__main__":
    main()
