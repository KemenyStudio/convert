import openpyxl

def convert_xlsx_to_txt(input_file, output_file_path):
    workbook = openpyxl.load_workbook(input_file)
    sheet = workbook.active
    txt_data = ''

    for row in sheet.iter_rows(values_only=True):
        txt_data += '\t'.join(map(str, row)) + '\n'

    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write(txt_data)