import pandas as pd
import os

def convert_xls_to_csv(input_file, output_dir):
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Read the XLS file
    xls_data = pd.read_excel(input_file, sheet_name=None)
    
    # Write each sheet to a separate CSV file
    output_files = []
    for sheet_name, data in xls_data.items():
        csv_file = os.path.join(output_dir, f"{os.path.splitext(input_file.filename)[0]}_{sheet_name}.csv")
        data.to_csv(csv_file, index=False)
        output_files.append(csv_file)
    
    return output_files