import shutil


def get_disk_metrics(path: str = "/") -> tuple[float, float, float]:
    """
    Calculates and returns total GiB, used GiB, and decimal usage ratio.
    """
    total_bytes, used_bytes, _ = shutil.disk_usage(path)

    gib_divisor = 2**30
    total_gib = total_bytes / gib_divisor
    used_gib = used_bytes / gib_divisor
    disk_decimal = used_bytes / total_bytes

    return total_gib, used_gib, disk_decimal


def print_disk_usage(
    total_gib: float,
    used_gib: float,
    disk_decimal: float,
    bar_length: int = 50
):
    """
    Formats and prints the disk usage progress bar.
    """
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
