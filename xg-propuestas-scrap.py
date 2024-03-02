## this app extracts content from https://xochitlgalvez.com/propuestas/


import streamlit as st
import requests
from bs4 import BeautifulSoup
import json

# Función para obtener las propuestas de la página
def obtener_propuestas(url):
    try:
        # Descargar el contenido HTML de la página
        respuesta = requests.get(url)
        if respuesta.status_code == 200:
            soup = BeautifulSoup(respuesta.text, 'html.parser')
            
            propuestas = []
        
            # Buscar todas las secciones de propuestas representadas por 'ea-body'
            for propuesta in soup.select('.ea-body'):
                # Intentar encontrar el título en el hermano anterior 'h3'
                titulo_elemento = propuesta.find_previous_sibling('h3')
                titulo = titulo_elemento.text.strip() if titulo_elemento else "Título no encontrado"
                contenido = propuesta.get_text(separator='\n', strip=True)
                propuestas.append({'titulo': titulo, 'contenido': contenido})
            
            return propuestas
        else:
            st.error(f"Error al cargar la página, código de estado HTTP: {respuesta.status_code}")
            return []
    except Exception as e:
        st.error(f"Error al obtener propuestas: {e}")
        return []

# Interfaz de usuario en Streamlit
st.title('Extractor de Propuestas de Sitio Web en Formato JSON')

# Entrada de URL por el usuario
url_usuario = st.text_input('Ingrese la URL del sitio del que desea extraer propuestas:', '')

if st.button('Obtener Propuestas'):
    if url_usuario:
        # Obtener y mostrar propuestas
        propuestas = obtener_propuestas(url_usuario)
        if propuestas:
            # Mostrar propuestas en la aplicación
            for propuesta in propuestas:
                st.subheader(propuesta['titulo'])
                st.write(propuesta['contenido'])
                st.write('---')  # Línea separadora

            # Guardar las propuestas en un archivo JSON
            with open('propuestas.json', 'w', encoding='utf-8') as f:
                json.dump(propuestas, f, ensure_ascii=False, indent=4)
            st.success("Propuestas guardadas en 'propuestas.json'.")
    else:
        st.warning('Por favor, ingrese una URL válida.')
