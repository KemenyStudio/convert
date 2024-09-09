import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_file):
    doc = fitz.open(stream=pdf_file.read())
    text_data = []

    for page in doc:
        text = page.get_text()
        text = ' '.join(text.split())
        text_data.append(text)

    doc.close()
    return text_data