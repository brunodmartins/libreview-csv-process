import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from process_glucose import GLUCOSE, RECORD_TYPE, TIMESTAMP


class ProcessGlucoseTest(unittest.TestCase):
    def test_cli_filters_records_from_inclusive_date(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "input.csv"
            output = Path(directory) / "output.csv"
            with source.open("w", encoding="utf-8-sig", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["LibreView export", "metadata"])
                writer.writerow([TIMESTAMP, RECORD_TYPE, GLUCOSE, "Other"])
                writer.writerow(["31-12-2023 23:59", "0", "70", "before"])
                writer.writerow(["01-01-2024 00:00", "0", "100", "boundary"])
                writer.writerow(["02-01-2024 12:00", "1", "110", "scan"])
                writer.writerow(["03-01-2024 12:00", "0", "120", "after"])

            subprocess.run(
                [sys.executable, "process_glucose.py", "--input", str(source), "--date", "2024-01-01", "--output", str(output)],
                check=True,
            )
            with output.open(encoding="utf-8", newline="") as file:
                self.assertEqual(list(csv.reader(file)), [
                    [TIMESTAMP, GLUCOSE],
                    ["01-01-2024 00:00", "100"],
                    ["03-01-2024 12:00", "120"],
                ])

    def test_rejects_input_as_output(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "input.csv"
            source.write_text("original", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "process_glucose.py", "--input", str(source), "--date", "2024-01-01", "--output", str(source)],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(source.read_text(encoding="utf-8"), "original")

    def test_rejects_date_without_hyphens(self):
        result = subprocess.run(
            [sys.executable, "process_glucose.py", "--input", "input.csv", "--date", "20240101", "--output", "output.csv"],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("YYYY-MM-DD", result.stderr)


if __name__ == "__main__":
    unittest.main()