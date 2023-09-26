import glob
import subprocess
from dataclasses import dataclass
from typing import Sequence, Optional

from typing import List


def _non_swap_system_devices() -> List[str]:
    """
    Returns a list of system-critical mount point devices.

    Checks common system directories such as '/', '/boot', '/home', etc.
    """
    system_devs = []

    with open('/proc/mounts', 'r') as f:
        for line in f:
            parts = line.split()
            device_path = parts[0]
            mount_point = parts[1]

            # Check if it's a system-critical mount point
            if mount_point in ['/', '/boot', '/home', '/var', '/usr', '/etc', '/bin', '/sbin']:
                system_devs.append(device_path)

    return system_devs


def _swap_devices() -> List[str]:
    """
    Returns a list of swap devices.
    """
    swap_devs = []

    with open('/proc/swaps', 'r') as f:
        # Skip header
        next(f)
        for line in f:
            parts = line.split()
            device_path = parts[0]
            # Swaps are considered as system devices
            swap_devs.append(device_path)

    return swap_devs


def system_devices() -> List[str]:
    """
    Retrieves a list of devices that are used by the Linux OS for critical functions.

    This includes primary mount points such as root, boot, home, etc., as well as swap devices.
    Additionally, provides WSL-specific adjustments.
    """
    system_devs = _non_swap_system_devices() + _swap_devices()

    # WSL-specific fix
    if is_wsl():
        system_devs.append('/dev/sda')

    return sorted(list(set(system_devs)))  # Remove duplicates


def get_devices(exclude_system_devices: bool = True) -> List[str]:
    """Return a list of all connected devices. If exclude_system_devices is True,
    exclude devices that are used by the system."""
    all_devices = glob.glob("/dev/sd[a-z]")

    if exclude_system_devices:
        system_devs = system_devices()
        all_devices = [device for device in all_devices if device not in system_devs]

    return all_devices


def is_wsl() -> bool:
    try:
        with open("/proc/version", "r") as f:
            return "microsoft" in f.read().lower()
    except FileNotFoundError:
        return False


@dataclass
class DriveInfo:
    device: str
    model: str
    model_family: str
    capacity: str
    serial_number: str
    power_on_hours: str


def info(device: str) -> DriveInfo:
    # Fetch drive details using smartctl
    result = subprocess.run(['smartctl', '-i', device], capture_output=True, text=True)
    output = result.stdout

    # Extract drive information
    model = _extract_info(output, "Device Model:")
    model_family = _extract_info(output, ["Vendor:", "Model Family:"])
    capacity = _extract_info(output, "User Capacity:").split('[')[-1].strip(']')
    serial_number = _extract_info(output, "Serial Number:")

    # Fetch Power_On_Hours separately
    result_power_on = subprocess.run(['smartctl', '-a', device], capture_output=True, text=True)
    power_on_hours = _extract_info(result_power_on.stdout, "Power_On_Hours")

    return DriveInfo(device=device, model=model, model_family=model_family, capacity=capacity,
                     serial_number=serial_number, power_on_hours=power_on_hours)


def _extract_info(output: str, keywords: list[str]) -> str:
    for line in output.splitlines():
        for keyword in keywords:
            if keyword in line:
                return line.split(':', 1)[-1].strip()
    return ''


if __name__ == '__main__':
    all_devs = get_devices(exclude_system_devices=False)
    print(all_devs)
    non_system_devs = get_devices(exclude_system_devices=True)
    print(non_system_devs)
