import os


def running_via_sudo() -> bool:
    return os.geteuid() == 0


def home_dir() -> str:
    if 'SUDO_USER' in os.environ:
        return os.path.expanduser(f"~{os.environ['SUDO_USER']}")
    else:
        return os.path.expanduser("~")
    