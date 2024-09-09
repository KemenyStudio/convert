from flask import Flask, request, render_template, jsonify, send_file, redirect, url_for
from utils.convert_xlsx_to_txt import convert_xlsx_to_txt
from utils.docx_to_json import docx_to_json
from utils.xml_to_json import xml_to_json
from utils.youtube_to_text import download_youtube_audio, transcribe_audio
from utils.pdf_to_json import extract_text_from_pdf
from utils.web_scraper import scrape_web_content
from utils.sitemap_scraper import handle_sitemap_url
from utils.xls_to_csv import convert_xls_to_csv
from utils.csv_to_json import convert_csv_to_json
from utils.audio_to_text import transcribe_audio as transcribe_audio_file

import os
import zipfile
import io
import tempfile
import json

app = Flask(__name__)

def check_env_file():
    return os.path.exists('.env')

@app.route('/')
def index():
    if not check_env_file():
        return redirect(url_for('setup'))
    return render_template('index.html')

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    if request.method == 'POST':
        api_key = request.form['api_key']  # General API Key
        region = request.form['region']
        language = request.form['language']
        azure_openai_endpoint = request.form.get('azure_openai_endpoint', '')
        azure_openai_api_version = request.form.get('azure_openai_api_version', '')
        azure_openai_chatgpt_deployment = request.form.get('azure_openai_chatgpt_deployment', '')
        azure_speech_key = request.form.get('azure_speech_key', '')  # Azure Speech Key
        azure_speech_region = request.form.get('azure_speech_region', '')
        youtube_api_key = request.form.get('youtube_api_key', '')  # YouTube API Key
        with open('.env', 'w') as f:
            f.write(f"API_KEY={api_key}\n")
            f.write(f"REGION={region}\n")
            f.write(f"LANGUAGE={language}\n")
            if azure_openai_endpoint:
                f.write(f"AZURE_OPENAI_ENDPOINT={azure_openai_endpoint}\n")
            if azure_openai_api_version:
                f.write(f"AZURE_OPENAI_API_VERSION={azure_openai_api_version}\n")
            if azure_openai_chatgpt_deployment:
                f.write(f"AZURE_OPENAI_CHATGPT_DEPLOYMENT={azure_openai_chatgpt_deployment}\n")
            if azure_speech_key:
                f.write(f"AZURE_SPEECH_KEY={azure_speech_key}\n")
            if azure_speech_region:
                f.write(f"AZURE_SPEECH_REGION={azure_speech_region}\n")
            if youtube_api_key:
                f.write(f"YOUTUBE_API_KEY={youtube_api_key}\n")
        return redirect(url_for('index'))

@app.route('/audio_to_text', methods=['POST'])
def audio_to_text():
    file = request.files['file']
    speech_key = os.getenv("AZURE_SPEECH_KEY", request.form.get('azure_speech_key'))
    service_region = os.getenv("AZURE_SPEECH_REGION", request.form.get('azure_speech_region'))
    return transcribe_audio_file(file, speech_key, service_region)

@app.route('/youtube_to_text', methods=['POST'])
def youtube_to_text():
    url = request.form['url']
    speech_key = os.getenv("AZURE_SPEECH_KEY", request.form.get('azure_speech_key'))
    service_region = os.getenv("AZURE_SPEECH_REGION", request.form.get('azure_speech_region'))
    audio_file = download_youtube_audio(url)
    if audio_file:
        return transcribe_audio(audio_file, speech_key, service_region)
    return "Error downloading YouTube audio", 500

@app.route('/convert_xlsx_to_txt', methods=['POST'])
def convert_xlsx_to_txt_route():
    files = request.files.getlist('file')
    output_files = []
    with tempfile.TemporaryDirectory() as temp_dir:
        for file in files:
            output_file_path = os.path.join(temp_dir, f"{file.filename.rsplit('.', 1)[0]}.txt")
            convert_xlsx_to_txt(file, output_file_path)
            output_files.append(output_file_path)
        
        # Create a zip file
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for output_file in output_files:
                zip_file.write(output_file, os.path.basename(output_file))
        zip_buffer.seek(0)
    
    return send_file(zip_buffer, as_attachment=True, download_name='converted_files.zip', mimetype='application/zip')

@app.route('/docx_to_json', methods=['POST'])
def docx_to_json_route():
    files = request.files.getlist('file')
    output_files = []
    with tempfile.TemporaryDirectory() as temp_dir:
        for file in files:
            output_file_path = os.path.join(temp_dir, f"{file.filename.rsplit('.', 1)[0]}.json")
            with open(output_file_path, 'w') as f:
                json.dump(docx_to_json(file), f)
            output_files.append(output_file_path)
        
        # Create a zip file
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for output_file in output_files:
                zip_file.write(output_file, os.path.basename(output_file))
        zip_buffer.seek(0)
    
    return send_file(zip_buffer, as_attachment=True, download_name='converted_files.zip', mimetype='application/zip')

@app.route('/xml_to_json', methods=['POST'])
def xml_to_json_route():
    files = request.files.getlist('file')
    output_files = []
    with tempfile.TemporaryDirectory() as temp_dir:
        for file in files:
            output_file_path = os.path.join(temp_dir, f"{file.filename.rsplit('.', 1)[0]}.json")
            with open(output_file_path, 'w') as f:
                json.dump(xml_to_json(file), f)
            output_files.append(output_file_path)
        
        # Create a zip file
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for output_file in output_files:
                zip_file.write(output_file, os.path.basename(output_file))
        zip_buffer.seek(0)
    
    return send_file(zip_buffer, as_attachment=True, download_name='converted_files.zip', mimetype='application/zip')

@app.route('/youtube_to_text', methods=['POST'])
def youtube_to_text_route():
    youtube_url = request.form['url']
    audio_file = download_youtube_audio(youtube_url)
    if audio_file is None:
        return jsonify({"error": "Failed to download YouTube audio"}), 400
    transcription = transcribe_audio(audio_file)
    
    # Create a zip file
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        zip_file.writestr('transcription.txt', transcription)
    zip_buffer.seek(0)
    
    return send_file(zip_buffer, as_attachment=True, download_name='transcription.zip', mimetype='application/zip')

@app.route('/pdf_to_json', methods=['POST'])
def pdf_to_json_route():
    files = request.files.getlist('file')
    output_files = []
    with tempfile.TemporaryDirectory() as temp_dir:
        for file in files:
            output_file_path = os.path.join(temp_dir, f"{file.filename.rsplit('.', 1)[0]}.json")
            with open(output_file_path, 'w') as f:
                json.dump(extract_text_from_pdf(file), f)
            output_files.append(output_file_path)
        
        # Create a zip file
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for output_file in output_files:
                zip_file.write(output_file, os.path.basename(output_file))
        zip_buffer.seek(0)
    
    return send_file(zip_buffer, as_attachment=True, download_name='converted_files.zip', mimetype='application/zip')

@app.route('/scrape_web_content', methods=['POST'])
def scrape_web_content_route():
    url = request.form['url']
    scraped_data = scrape_web_content(url)
    
    # Create a zip file
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        zip_file.writestr('scraped_content.json', json.dumps(scraped_data))
    zip_buffer.seek(0)
    
    return send_file(zip_buffer, as_attachment=True, download_name='scraped_content.zip', mimetype='application/zip')

@app.route('/sitemap_scraper', methods=['POST'])
def sitemap_scraper_route():
    sitemap_url = request.form['url']
    scraped_data = handle_sitemap_url(sitemap_url)
    
    # Create a zip file
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        zip_file.writestr('sitemap_content.json', json.dumps(scraped_data))
    zip_buffer.seek(0)
    
    return send_file(zip_buffer, as_attachment=True, download_name='sitemap_content.zip', mimetype='application/zip')

@app.route('/audio_to_text', methods=['POST'])
def audio_to_text_route():
    files = request.files.getlist('file')
    output_files = []
    with tempfile.TemporaryDirectory() as temp_dir:
        for file in files:
            transcription = transcribe_audio_file(file)
            output_file_path = os.path.join(temp_dir, f"{file.filename.rsplit('.', 1)[0]}.txt")
            with open(output_file_path, 'w') as f:
                f.write(transcription)
            output_files.append(output_file_path)
        
        # Create a zip file
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for output_file in output_files:
                zip_file.write(output_file, os.path.basename(output_file))
        zip_buffer.seek(0)
    
    return send_file(zip_buffer, as_attachment=True, download_name='transcriptions.zip', mimetype='application/zip')

@app.route('/convert_xls_to_csv', methods=['POST'])
def convert_xls_to_csv_route():
    files = request.files.getlist('file')
    output_files = []
    with tempfile.TemporaryDirectory() as temp_dir:
        for file in files:
            output_files.extend(convert_xls_to_csv(file, temp_dir))
        
        # Create a zip file
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for output_file in output_files:
                zip_file.write(output_file, os.path.basename(output_file))
        zip_buffer.seek(0)
    
    return send_file(zip_buffer, as_attachment=True, download_name='converted_files.zip', mimetype='application/zip')

@app.route('/convert_csv_to_json', methods=['POST'])
def convert_csv_to_json_route():
    files = request.files.getlist('file')
    output_files = []
    with tempfile.TemporaryDirectory() as temp_dir:
        for file in files:
            output_file_path = os.path.join(temp_dir, f"{file.filename.rsplit('.', 1)[0]}.json")
            with open(output_file_path, 'w', encoding='utf-8') as f:
                json.dump(convert_csv_to_json(file), f)
            output_files.append(output_file_path)
        
        # Create a zip file
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for output_file in output_files:
                zip_file.write(output_file, os.path.basename(output_file))
        zip_buffer.seek(0)
    
    return send_file(zip_buffer, as_attachment=True, download_name='converted_files.zip', mimetype='application/zip')

if __name__ == '__main__':
    app.run(debug=True)