# libreview-csv-process
A Python script to process and filter the data from LibreView

## Usage

Requires Python 3. Run:

```sh
python3 process_glucose.py --input INPUT.csv --date YYYY-MM-DD --output OUTPUT.csv
```

The output contains the device timestamp and historical glucose value for record
type 0, starting on the given date (inclusive). The original timestamp format is
preserved. The input and output files must be different.

Run the tests with `python3 -m unittest -v`.
