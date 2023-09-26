import datetime


def log(device: str, drive_logfile: str, message: str):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    formatted_message = f"[{timestamp}][{device}] {message}"
    print(formatted_message)
    with open(drive_logfile, 'a') as f:
        f.write(formatted_message + "\n")

