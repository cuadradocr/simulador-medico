import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
from streamlit_mic_recorder import speech_to_text

st.set_page_config(page_title="Simulador Voz: Jeferson", layout="centered")

# Conexión con Secrets
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.error("⚠️ Configura la GEMINI_API_KEY en Secrets.")
    st.stop()

if "entrenado" not in st.session_state:
    st.session_state.entrenado = False

st.title("🎙️ Entrenamiento de Voz")

# Modelo rápido
model = genai.GenerativeModel('gemini-1.5-flash')

# 1. Carga del Manual
if not st.session_state.entrenado:
    archivo = st.file_uploader("Sube el PDF de Filinar G", type="pdf")
    if archivo:
        reader = PdfReader(archivo)
        st.session_state.pdf_text = "".join([p.extract_text() for p in reader.pages])[:8000]
        
        res = model.generate_content("Eres un Pediatra. Saluda a Jeferson Cuadrado de forma muy breve.")
        st.session_state.entrenado = True
        
        # FORZADO DE AUDIO INICIAL
        audio_url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={res.text[:200]}&tl=es&client=tw-ob"
        st.write("🔊 **Escucha al Doctor ahora...**")
        st.audio(audio_url, format="audio/mp3", autoplay=True)
        st.rerun()

# 2. Interacción por Voz
if st.session_state.entrenado:
    st.markdown("### 👨‍⚕️ El Doctor te está escuchando...")
    
    # Botón de micrófono
    texto_voz = speech_to_text(language='es', start_prompt="🎤 TOCAR PARA HABLAR", stop_prompt="⏹️ ENVIAR", key='speech')

    if texto_voz:
        historial = f"Eres Pediatra. Jeferson dice: '{texto_voz}'. Responde breve con el manual: {st.session_state.pdf_text}"
        respuesta = model.generate_content(historial)
        
        # VOZ DEL DOCTOR
        t_voz = respuesta.text.replace('*', '')
        audio_url_res = f"https://translate.google.com/translate_tts?ie=UTF-8&q={t_voz[:200]}&tl=es&client=tw-ob"
        
        st.write("🔊 **Reproduciendo respuesta...**")
        st.audio(audio_url_res, format="audio/mp3", autoplay=True)
        # Dejamos el texto visible por si los audífonos fallan
        st.info(f"Doctor dice: {respuesta.text}")
