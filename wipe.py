#!/usr/bin/env python3

import os
import subprocess

import drive
import user
from log import log


def main():
    # Base directory for log files
    user_home_dir = user.home_dir()
    logdir = os.path.join(user_home_dir, "Desktop/wipe-logs")

    # Ensure the log directory exists
    os.makedirs(logdir, exist_ok=True)

    # Change ownership of the log directory to the actual user if sudo is used
    if 'SUDO_USER' in os.environ:
        os.chown(logdir, int(os.environ['SUDO_UID']), int(os.environ['SUDO_GID']))

    # Get the system drive
    system_device = drive.system_device()

    log("/dev/stdout", "/dev/stdout", f"System Drive: {system_device}")

    # List all available drives except the system drive
    for device in [f"/dev/sd{chr(i)}" for i in range(97, 123)]:  # sd[a-z]
        if not device.startswith(system_device):
            drive_info = subprocess.check_output(f"smartctl -i {device}", shell=True).decode().splitlines()
            model = next((line.split(":")[1].strip() for line in drive_info if "Device Model:" in line), "Unknown")
            vendor_or_family = next(
                (line.split(":")[1].strip() for line in drive_info if "Vendor:" in line or "Model Family:" in line),
                "Unknown")
            capacity = next((line.split("[")[1].split("]")[0] for line in drive_info if "User Capacity:" in line),
                            "Unknown")
            serial = next((line.split(":")[1].strip() for line in drive_info if "Serial Number:" in line), "Unknown")

            logfile_name = f"{vendor_or_family}_{serial}_{capacity}".replace(' ', '_').replace('/', '_')
            logfile = os.path.join(logdir, f"{logfile_name}.log")

            # Change ownership of the logfile to the actual user if sudo is used
            if 'SUDO_USER' in os.environ and not os.path.exists(logfile):
                with open(logfile, 'w') as f:
                    os.chown(logfile, int(os.environ['SUDO_UID']), int(os.environ['SUDO_GID']))

            log(device, "/dev/stdout", f"Logging to: {logfile}")

            # Log drive details
            power_on_hours = subprocess.check_output(
                f"smartctl -a {device} | grep 'Power_On_Hours' | awk '{{print $10}}'", shell=True).decode().strip()

            log_entries = [
                f"Wiping Drive: {device}",
                f"Model: {model}",
                f"Vendor or Family: {vendor_or_family}",
                f"Capacity: {capacity}",
                f"Serial Number: {serial}",
                f"Power On Hours: {power_on_hours}"
            ]

            for entry in log_entries:
                log(device, logfile, entry)

            # Wipe the drive
            result = subprocess.run(["dd", "if=/dev/zero", f"of={device}", "bs=1M"], stderr=subprocess.PIPE, text=True)

            if "No space left on device" in result.stderr:
                log(device, logfile, f"Successfully wiped {device}")
            elif result.returncode != 0:
                log(device, logfile, f"Error occurred while wiping {device}")
                log(device, logfile, result.stderr)
            else:
                log(device, logfile, f"Successfully wiped {device}")

            log(device, logfile, "-----------------------")

    log("/dev/stdout", "/dev/stdout", f"All drive wipes have been completed. Check individual logs in {logdir}")


if __name__ == "__main__":
    main()
