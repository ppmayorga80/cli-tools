#!/usr/bin/env python3
"""
Change EC2 instance type based on schedule or manual override.

Usage:
  ec2_type_switcher.py [--instance-id=<id>] --type=<type> [--dry-run]
  ec2_type_switcher.py [--instance-id=<id>] --csv=<path> [--dry-run]
  ec2_type_switcher.py --manual | --auto | --mode
  ec2_type_switcher.py [--instance-id=<id>] --query

Options:
  -i,--instance-id=<id>   EC2 instance ID (e.g., i-0123456789abcdef0) [default: i-0f9a79684854379b0]
  -t,--type=<type>        Manually set the instance type (overrides schedule), e.g., t2.small
  --csv=<path>            Path to schedule CSV file [default: DEFAULT]
  --dry-run               Simulate changes without applying them
  -m,--manual             Set S3 mode to manual and exit (writes s3://mis15tours/ec2_mode.json -> {"mode":"manual"})
  -a,--auto               Set S3 mode to auto and exit (writes s3://mis15tours/mode.json -> {"mode":"auto"})
  -r,--mode               Get S3 mode and exit (reads s3://mis15tours/mode.json)
  --query                 Print current instance type and exit

CSV mode guard:
  CSV mode (no --type) will ONLY run if s3://mis15tours/ec2_mode.json contains {"mode":"auto"}.
"""

import json
import os.path
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import smart_open
from docopt import docopt
import boto3
from botocore.exceptions import ClientError

FAMILY_ARCH = {
    "t2": "x86_64",
    "t3": "x86_64",
    "t3a": "x86_64",
    "t4g": "arm64",
}

S3_PATH = "s3://mis15tours/ec2_mode.json"


def set_manual_mode():
    with smart_open.open(S3_PATH, "w") as f:
        data = json.dumps({"mode": "manual"})
        f.write(data)


def set_auto_mode():
    with smart_open.open(S3_PATH, "w") as f:
        data = json.dumps({"mode": "auto"})
        f.write(data)


def get_mode():
    with smart_open.open(S3_PATH, "r") as f:
        try:
            data = json.loads(f.read())
            return data["mode"]
        except Exception as e:
            print(f"Can't parse '{S3_PATH}': {e}")
    return ""


def can_run_in_automatic():
    with smart_open.open(S3_PATH, "r") as f:
        try:
            data = json.loads(f.read())
            if data.get["mode"] == "auto":
                return True
        except Exception as e:
            print(f"Can't parse '{S3_PATH}': {e}")

    return False


def family_of(inst_type: str) -> str:
    return inst_type.split(".")[0]


def arch_for_family(fam: str) -> str | None:
    return FAMILY_ARCH.get(fam)


def now_in_monterrey():
    return datetime.now(ZoneInfo("America/Monterrey"))


def load_schedule(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    required_cols = {"Day", "Start", "End", "EC2_Type"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"CSV must include these columns: {required_cols}")
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
            val = row["EC2_Type"].strip().lower()
            if val in {"stop", "nan", ""}:
                return "STOP"
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


def stop_instance(ec2, instance_id: str, dry_run: bool):
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


# ---------- main ----------
def main():
    args = docopt(__doc__)

    instance_id = args["--instance-id"]
    manual_type = args["--type"]
    csv_path = args["--csv"]
    dry_run = args["--dry-run"]
    flag_manual = args["--manual"]
    flag_auto = args["--auto"]
    flag_mode = args["--mode"]
    flag_query = args["--query"]

    if flag_query:
        if not instance_id:
            raise SystemExit("You must provide --instance-id with --query.")
        ec2 = boto3.client("ec2", region_name="us-east-1")
        desc = get_instance_description(ec2, instance_id)
        print(f"[INFO] Instance {instance_id} type is: {desc['InstanceType']}")
        return

    if flag_manual and flag_auto:
        raise SystemExit("Provide only one of --manual or --auto, not both.")
    # Handle mode-set operations and exit
    if flag_manual:
        set_manual_mode()
        print("[INFO] Manual Mode is enabled.")
        return
    if flag_auto:
        set_auto_mode()
        print("[INFO] Automatic Mode is enabled.")
        return
    if flag_mode:
        current_mode = get_mode()
        print(f"[INFO] Current Mode is: '{current_mode}'")
        return

    ec2 = boto3.client("ec2", region_name="us-east-1")

    # Determine desired type: manual override > schedule (CSV) > default
    if manual_type:
        desired_type = manual_type.strip()
        source = "manual override (--type)"
        # Manual override proceeds regardless of S3 mode guard
    else:
        # CSV mode is gated by S3 ec2_mode.json == {"mode":"auto"}
        if not can_run_in_automatic():
            raise SystemExit(
                f"CSV mode disabled: '{S3_PATH}' is set to manual. "
                "Use --manual/--auto to change mode if needed."
            )
        if csv_path == "DEFAULT":
            csv_path = os.path.join(os.path.dirname(__file__), "ec2_schedule.csv")
        schedule_df = load_schedule(csv_path)
        now = now_in_monterrey()
        desired_type = desired_type_for_now(schedule_df, default_type, now)
        source = f"schedule file '{os.path.basename(csv_path)}'"

    inst = get_instance_description(ec2, instance_id)
    current_type = inst["InstanceType"]

    now_log = now_in_monterrey()
    print(f"[INFO] Current time: {now_log.isoformat()} (America/Monterrey)")
    print(f"[INFO] Current type: {current_type} | Desired type: {desired_type} (source: {source})")

    # Handle STOP case from schedule
    if desired_type == "STOP":
        print("[INFO] Schedule requests STOP. Stopping instance...")
        stop_instance(ec2, instance_id, dry_run)
        print("[DONE] Instance stopped per schedule.")
        return

    if desired_type == current_type:
        print("[INFO] No change required.")
        return

    if is_in_asg(inst):
        raise SystemExit(
            "The instance belongs to an Auto Scaling Group; modify the Launch Template/Configuration instead."
        )

    ok, msg = ensure_compatible(desired_type, inst, ec2)
    if not ok:
        raise SystemExit(f"Compatibility check failed: {msg}")
    else:
        print(f"[INFO] Compatibility: {msg}")

    stop_modify_start(ec2, instance_id, current_type, desired_type, dry_run)
    print("[DONE] Change applied.")


if __name__ == "__main__":
    main()
