from docx import Document
import json

def docx_to_json(docx_file):
    doc = Document(docx_file)
    data = [{"text": para.text, "style": para.style.name} for para in doc.paragraphs]
    return data