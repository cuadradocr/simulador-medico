import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
from streamlit_mic_recorder import speech_to_text

st.set_page_config(page_title="Visita Médica: Jeferson", layout="centered")

# 1. Configuración de API Key (Secrets)
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.error("⚠️ Configura GEMINI_API_KEY en los Secrets de Streamlit.")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "entrenado" not in st.session_state:
    st.session_state.entrenado = False

st.title("🎙️ Visita Médica: Jeferson Cuadrado")

# 2. Selección Automática de Modelo (Para evitar el Error 404)
if "modelo_nombre" not in st.session_state:
    try:
        modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        st.session_state.modelo_nombre = next((m for m in modelos if '1.5-flash' in m), modelos[0])
    except:
        st.session_state.modelo_nombre = "models/gemini-1.5-flash"

model = genai.GenerativeModel(st.session_state.modelo_nombre)

# 3. Carga de Manual
if not st.session_state.entrenado:
    archivo = st.file_uploader("Sube el PDF de Filinar G", type="pdf")
    if archivo:
        with st.spinner("El Doctor está leyendo..."):
            reader = PdfReader(archivo)
            st.session_state.pdf_text = "".join([p.extract_text() for p in reader.pages])[:8000]
            
            # Saludo inicial
            res = model.generate_content(f"Eres un Pediatra. Saluda a Jeferson Cuadrado de forma breve y natural.")
            st.session_state.messages.append({"role": "assistant", "content": res.text})
            st.session_state.entrenado = True
            
            # Audio automático
            st.audio(f"https://translate.google.com/translate_tts?ie=UTF-8&q={res.text[:200]}&tl=es&client=tw-ob", autoplay=True)
            st.rerun()

# 4. Interacción por Voz
if st.session_state.entrenado:
    st.markdown("### 👨‍⚕️ El Doctor te está escuchando...")
    
    # Este botón detecta tu voz a través de los audífonos
    texto_voz = speech_to_text(
        language='es',
        start_prompt="🎤 TOCAR PARA HABLAR",
        stop_prompt="⏹️ ENVIAR AL DOCTOR",
        key='speech'
    )

    if texto_voz:
        # El doctor responde basándose en lo que tú dijiste y el manual
        contexto = f"Eres Pediatra. Jeferson dice: '{texto_voz}'. Responde brevemente usando este manual: {st.session_state.pdf_text}"
        respuesta = model.generate_content(contexto)
        
        st.session_state.messages.append({"role": "assistant", "content": respuesta.text})
        
        # Audio de respuesta del doctor
        t_voz = respuesta.text.replace('*', '')
        st.audio(f"https://translate.google.com/translate_tts?ie=UTF-8&q={t_voz[:200]}&tl=es&client=tw-ob", autoplay=True)
        
        # Muestra el texto por si el audio no se oye bien
        st.info(f"Doctor: {respuesta.text}")

    if st.sidebar.button("🗑️ Reiniciar Sesión"):
        st.session_state.clear()
        st.rerun()
