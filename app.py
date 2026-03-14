import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
from streamlit_mic_recorder import speech_to_text

st.set_page_config(page_title="Simulador de Voz", layout="centered")

# Cargar API Key desde Secrets
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.error("⚠️ Configura la API KEY en Secrets de Streamlit.")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "entrenado" not in st.session_state:
    st.session_state.entrenado = False

st.title("🎙️ Visita Médica: Jeferson Cuadrado")

model = genai.GenerativeModel('gemini-1.5-flash')

# Paso 1: Carga del Manual
if not st.session_state.entrenado:
    archivo = st.file_uploader("Sube el PDF para activar al doctor", type="pdf")
    if archivo:
        reader = PdfReader(archivo)
        st.session_state.pdf_text = "".join([p.extract_text() for p in reader.pages])
        
        res = model.generate_content(f"Eres un Pediatra. Saluda a Jeferson Cuadrado de forma breve. Manual: {st.session_state.pdf_text[:5000]}")
        st.session_state.messages.append({"role": "assistant", "content": res.text})
        st.session_state.entrenado = True
        
        # Audio de bienvenida
        st.audio(f"https://translate.google.com/translate_tts?ie=UTF-8&q={res.text[:200]}&tl=es&client=tw-ob", autoplay=True)
        st.rerun()

# Paso 2: El micrófono directo
if st.session_state.entrenado:
    st.write("### 👨‍⚕️ El Doctor está esperando...")
    
    # Este componente convierte tu voz a texto directamente
    texto_voz = speech_to_text(
        language='es',
        start_prompt="🎤 TOCAR PARA HABLAR (Usa tus audífonos)",
        stop_prompt="⏹️ PARAR",
        key='speech'
    )

    if texto_voz:
        st.session_state.messages.append({"role": "user", "content": texto_voz})
        
        contexto = f"Eres Pediatra. Jeferson dice: {texto_voz}. Manual: {st.session_state.pdf_text[:5000]}"
        respuesta = model.generate_content(contexto)
        
        st.session_state.messages.append({"role": "assistant", "content": respuesta.text})
        
        # Reproducir respuesta
        st.audio(f"https://translate.google.com/translate_tts?ie=UTF-8&q={respuesta.text[:200]}&tl=es&client=tw-ob", autoplay=True)
        st.rerun()
