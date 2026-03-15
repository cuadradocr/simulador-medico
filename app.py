import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
from streamlit_mic_recorder import speech_to_text
import base64

st.set_page_config(page_title="Simulador Voz: Jeferson", layout="centered")

# Configuración de API
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.error("⚠️ Revisa la GEMINI_API_KEY en Secrets.")
    st.stop()

if "entrenado" not in st.session_state:
    st.session_state.entrenado = False

# ELIMINADOR DE ERROR NOTFOUND: Usamos el nombre exacto del modelo actual
model = genai.GenerativeModel('gemini-1.5-flash-latest')

def reproducir_audio(texto):
    # Genera el enlace de audio y lo muestra como un reproductor visible
    audio_url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={texto[:200]}&tl=es&client=tw-ob"
    st.audio(audio_url, format="audio/mp3", autoplay=True)

st.title("🎙️ Entrenamiento de Voz")

# 1. Carga del Manual
if not st.session_state.entrenado:
    archivo = st.file_uploader("Sube el PDF de Filinar G", type="pdf")
    if archivo:
        reader = PdfReader(archivo)
        st.session_state.pdf_text = "".join([p.extract_text() for p in reader.pages])[:8000]
        
        try:
            res = model.generate_content("Eres un Pediatra. Saluda a Jeferson Cuadrado de forma muy breve.")
            st.session_state.entrenado = True
            st.success("¡Doctor conectado!")
            reproducir_audio(res.text)
            st.rerun()
        except Exception as e:
            st.error(f"Error de conexión: {e}")

# 2. Interacción por Voz
if st.session_state.entrenado:
    st.markdown("### 👨‍⚕️ El Doctor te escucha...")
    
    # Botón de micrófono
    texto_voz = speech_to_text(language='es', start_prompt="🎤 TOCAR PARA HABLAR", stop_prompt="⏹️ ENVIAR", key='speech')

    if texto_voz:
        prompt = f"Eres Pediatra. Jeferson dice: '{texto_voz}'. Responde breve con el manual: {st.session_state.pdf_text}"
        respuesta = model.generate_content(prompt)
        
        # Mostrar respuesta y forzar audio
        st.info(f"Doctor dice: {respuesta.text}")
        reproducir_audio(respuesta.text)
