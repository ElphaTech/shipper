from textual.widgets import ProgressBar
from .disk_stats import get_disk_metrics


class DiskSpaceBar(ProgressBar):
    def check_space(self) -> None:
        total, used, pct = get_disk_metrics()
        self.update(
            total=total,
            progress=used
        )

    def on_mount(self) -> None:
        """Called when widget first attached."""

        self.check_space()

        self.set_interval(15, self.check_space)
