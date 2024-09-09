import csv
import io

def convert_csv_to_json(csv_file):
    csv_file.seek(0)  # Ensure we're at the start of the file
    try:
        text_stream = io.TextIOWrapper(csv_file, encoding='utf-8')
        reader = csv.DictReader(text_stream)
        return [row for row in reader]
    except UnicodeDecodeError:
        csv_file.seek(0)
        text_stream = io.TextIOWrapper(csv_file, encoding='latin1')
        reader = csv.DictReader(text_stream)
        return [row for row in reader]