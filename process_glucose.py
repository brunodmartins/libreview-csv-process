import argparse
import csv
from datetime import date, datetime
from pathlib import Path


TIMESTAMP = "Carimbo de data/hora do dispositivo"
RECORD_TYPE = "Tipo de registro"
GLUCOSE = "Histórico de glicose mg/dL"


def parse_date(value):
    try:
        parsed = date.fromisoformat(value)
        if parsed.isoformat() != value:
            raise ValueError("date is not in YYYY-MM-DD format")
        return parsed
    except ValueError as error:
        raise argparse.ArgumentTypeError("date must be in YYYY-MM-DD format") from error


def process_csv(input_path, start_date, output_path):
    if input_path.resolve() == output_path.resolve():
        raise ValueError("input and output files must be different")

    with input_path.open(encoding="utf-8-sig", newline="") as source:
        next(source)
        reader = csv.DictReader(source)
        required = {TIMESTAMP, RECORD_TYPE, GLUCOSE}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError("input CSV is missing required columns")

        with output_path.open("w", encoding="utf-8", newline="") as destination:
            writer = csv.DictWriter(destination, fieldnames=[TIMESTAMP, GLUCOSE])
            writer.writeheader()
            for row in reader:
                if row[RECORD_TYPE] == "0":
                    timestamp = datetime.strptime(row[TIMESTAMP], "%d-%m-%Y %H:%M")
                    if timestamp.date() >= start_date:
                        writer.writerow({TIMESTAMP: row[TIMESTAMP], GLUCOSE: row[GLUCOSE]})


def main():
    parser = argparse.ArgumentParser(description="Filter LibreView glucose history records.")
    parser.add_argument("--input", type=Path, required=True, help="input LibreView CSV file")
    parser.add_argument("--date", type=parse_date, required=True, help="inclusive start date (YYYY-MM-DD)")
    parser.add_argument("--output", type=Path, required=True, help="output CSV file")
    args = parser.parse_args()
    try:
        process_csv(args.input, args.date, args.output)
    except (OSError, ValueError, StopIteration) as error:
        parser.exit(1, f"error: {error or 'input CSV is empty'}\n")


if __name__ == "__main__":
    main()