import glob
import subprocess


def system_device() -> str:
    return subprocess.check_output("df / | tail -1 | awk '{print $1}' | sed 's/[0-9]*$//'",
                                   shell=True).decode().strip()


def get_devices(exclude_system_device: bool = True) -> list[str]:
    all_devices = glob.glob("/dev/sd[a-z]")

    if exclude_system_device:
        root_device = system_device()
        all_devices = [device for device in all_devices if device != root_device]

    return all_devices
