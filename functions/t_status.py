import json
import os
from textual.widgets import DataTable

from .config import DATA_FILE_PATH, load_config
from .t_status_data import get_data_table, get_overview_data_table

CONFIG = load_config()


class StatusTable(DataTable):
    """A custom widget for displaying data from a dynamically updating JSON file."""

    # Store the last known modification time of the file
    last_mtime: float = 0.0

    def load_data_from_json(self) -> None:
        """Reads and updates the table content from the JSON file."""
        try:
            # Check if file has been modified recently
            current_mtime = os.path.getmtime(DATA_FILE_PATH)
            if current_mtime <= self.last_mtime:
                return  # Skip if not modified
            self.last_mtime = current_mtime

            # Get new data
            with open(DATA_FILE_PATH, "r") as f:
                try:
                    data = json.load(f)
                except Exception:
                    return
            if not data:
                return  # Skip if data is empty
            filtered_data = get_data_table(data)

            # Add new data
            data_uids = filtered_data.keys()
            current_table_uids = self.rows.keys()
            uids_to_add = [i for i in data_uids if i not in current_table_uids]
            for uid in uids_to_add:
                self.add_row(*filtered_data[uid].values(), key=uid, label=uid)

            # Remove old data
            uids_to_remove = [
                i for i in current_table_uids if i not in data_uids]
            for uid in uids_to_remove:
                self.remove_row(uid)

            # Edit changed data
            uids_to_edit = [
                i for i in data_uids
                if i not in uids_to_add
                and i not in uids_to_remove
            ]
            for uid in uids_to_edit:
                for c_no in range(len(CONFIG.textual_columns)):
                    self.update_cell(
                        uid,
                        str(c_no),
                        filtered_data[uid][CONFIG.textual_columns[c_no]]
                    )

        except FileNotFoundError:
            # Optional: Display a message if the file is missing
            self.app.log(f"JSON file not found: {DATA_FILE_PATH}")
        except Exception as e:
            self.app.log(f"Error loading JSON data: {e}")

    def on_mount(self) -> None:
        """Called when the widget is first attached to the app."""

        columns = CONFIG.textual_columns
        for c_no in range(len(columns)):
            self.add_column(columns[c_no], key=str(c_no))

        self.load_data_from_json()

        self.set_interval(1, self.load_data_from_json)


class OverviewTable(DataTable):
    """A custom widget for displaying data from a dynamically updating JSON file."""

    # Store the last known modification time of the file
    last_mtime: float = 0.0

    def load_data_from_json(self) -> None:
        """Reads and updates the table content from the JSON file."""
#        try:
        # Check if file has been modified recently
        current_mtime = os.path.getmtime(DATA_FILE_PATH)
        if current_mtime <= self.last_mtime:
            return  # Skip if not modified
        self.last_mtime = current_mtime

        # Get new data
        with open(DATA_FILE_PATH, "r") as f:
            try:
                data = json.load(f)
            except Exception:
                return
        if not data:
            return  # Skip if data is empty
        filtered_data = get_overview_data_table(data)

        # Add new data
        data_uids = filtered_data.keys()
        current_table_uids = self.rows.keys()
        uids_to_add = [i for i in data_uids if i not in current_table_uids]
        for uid in uids_to_add:
            self.add_row(*filtered_data[uid].values(), key=uid, label=uid)

        # Remove old data
        uids_to_remove = [
            i for i in current_table_uids if i not in data_uids]
        for uid in uids_to_remove:
            self.remove_row(uid)

        # Edit changed data
        uids_to_edit = [
            i for i in data_uids
            if i not in uids_to_add
            and i not in uids_to_remove
        ]
        for uid in uids_to_edit:
            for c_no in range(len(CONFIG.textual_overview_columns)):
                self.update_cell(
                    uid,
                    str(c_no),
                    filtered_data[uid][
                        CONFIG.textual_overview_columns[c_no]]
                )

#        except FileNotFoundError:
#            # Optional: Display a message if the file is missing
#            self.app.log(f"JSON file not found: {DATA_FILE_PATH}")
#        except Exception as e:
#            self.app.log(f"Error loading JSON data: {e}")

    def on_mount(self) -> None:
        """Called when the widget is first attached to the app."""

        columns = CONFIG.textual_overview_columns
        for c_no in range(len(columns)):
            self.add_column(columns[c_no], key=str(c_no))

        self.load_data_from_json()

        self.set_interval(1, self.load_data_from_json)
