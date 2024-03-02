import streamlit as st
import fitz  # PyMuPDF
import json

def extraer_texto_pdf(archivo_pdf):
    """Extrae el texto de cada página de un archivo PDF."""
    try:
        # Abrir el PDF
        doc = fitz.open(stream=archivo_pdf.read())
        texto_completo = []
        
        # Extraer texto de cada página
        for pagina in doc:
            texto = pagina.get_text()
            # Remove extra whitespace and newline characters
            texto = ' '.join(texto.split())
            texto_completo.append(texto)
        
        doc.close()
        return texto_completo
    except Exception as e:
        st.error(f"Error al extraer texto: {e}")
        return []

st.title('Extractor de Texto de PDF a JSON')

archivo_pdf = st.file_uploader("Cargue un archivo PDF", type=['pdf'])

if archivo_pdf is not None:
    texto_pdf = extraer_texto_pdf(archivo_pdf)
    
    if texto_pdf:
        # Mostrar texto extraído
        st.write("Texto extraído del PDF:")
        for pagina, texto in enumerate(texto_pdf, start=1):
            st.write(f"**Página {pagina}:**")
            st.write(texto)
        
        # Guardar en JSON
        nombre_archivo_json = "texto_extraido.json"
        with open(nombre_archivo_json, "w", encoding="utf-8") as archivo_json:
            json.dump(texto_pdf, archivo_json, ensure_ascii=False, indent=4)
        
        st.success(f"Texto extraído guardado en {nombre_archivo_json}.")