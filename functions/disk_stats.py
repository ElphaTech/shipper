import shutil
from pathlib import Path


def bytes_to_gib(no_of_bytes: float) -> float:
    """
    Function to convert bytes to gigibytes.
    """
    return no_of_bytes / 2**30


def gib_to_bytes(no_of_gib: float) -> float:
    """
    Function to convert gigibytes to bytes.
    """
    return no_of_gib * 2**30


def get_file_size(path: str) -> float:
    """
    Function to get size of a file.
    Returns answer in bytes.
    """
    return Path(path).stat().st_size


def get_disk_metrics(path: str = "/") -> tuple[float, float, float]:
    """
    Calculates and returns total bytes, used bytes, and decimal usage ratio.
    """
    total_bytes, used_bytes, _ = shutil.disk_usage(path)

    disk_decimal = used_bytes / total_bytes

    return total_bytes, used_bytes, disk_decimal


def check_enough_space(path: str, buffer: float = 0) -> bool:
    """
    Function to check if duplicating a file will exceed the disk space.
    Buffer should be in bytes.
    Buffer is first removed from disk space.
    Returns boolean (true if there is enough space).
    """
    file_size = get_file_size(path)
    disk_space, used_disk, _ = get_disk_metrics()
    final_disk_space = disk_space - used_disk - buffer - file_size
    return final_disk_space > 0


def print_disk_usage(
    total_bytes: float,
    used_bytes: float,
    disk_decimal: float,
    bar_length: int = 50
):
    """
    Formats and prints the disk usage progress bar.
    """
    total_gib = bytes_to_gib(total_bytes)
    used_gib = bytes_to_gib(used_bytes)

    used_disk_count = int(disk_decimal * bar_length)

    used_disk_str = '#' * used_disk_count
    free_disk_str = ' ' * (bar_length - used_disk_count)

    print(
        f"Disk Space [{used_disk_str}{free_disk_str}] "
        f"{(disk_decimal * 100):5.1f}% "
        f"{used_gib:,.1f}GiB / {total_gib:,.1f}GiB"
    )


if __name__ == "__main__":
    print_disk_usage(
        *get_disk_metrics(), 20
    )
