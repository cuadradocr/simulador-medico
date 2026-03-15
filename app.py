import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
from streamlit_mic_recorder import speech_to_text

st.set_page_config(page_title="Entrenamiento: Jeferson", layout="centered")

# 1. Configuración de API
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.error("⚠️ Configura la GEMINI_API_KEY en los Secrets de Streamlit.")
    st.stop()

# 2. Selección automática del modelo para evitar errores 404
if "modelo_nombre" not in st.session_state:
    try:
        modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        st.session_state.modelo_nombre = next((m for m in modelos if '1.5-flash' in m), modelos[0])
    except:
        st.session_state.modelo_nombre = "models/gemini-1.5-flash"

model = genai.GenerativeModel(st.session_state.modelo_nombre)

if "entrenado" not in st.session_state:
    st.session_state.entrenado = False

st.title("🎙️ Visita Médica: Jeferson Cuadrado")

# 3. Carga del Manual (Optimizado para no agotar recursos)
if not st.session_state.entrenado:
    archivo = st.file_uploader("Sube el PDF para activar al doctor", type="pdf")
    if archivo:
        with st.spinner("El Doctor está analizando el manual..."):
            reader = PdfReader(archivo)
            # Solo cargamos lo esencial para evitar el error ResourceExhausted
            st.session_state.pdf_text = "".join([p.extract_text() for p in reader.pages])[:7000]
            
            res = model.generate_content("Eres un Pediatra amable. Saluda a Jeferson Cuadrado de forma muy breve.")
            st.session_state.entrenado = True
            
            # Audio automático
            audio_url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={res.text[:200]}&tl=es&client=tw-ob"
            st.audio(audio_url, format="audio/mp3", autoplay=True)
            st.rerun()

# 4. Interacción por Voz
if st.session_state.entrenado:
    st.markdown("### 👨‍⚕️ El Doctor te escucha...")
    
    texto_voz = speech_to_text(language='es', start_prompt="🎤 TOCAR PARA HABLAR", stop_prompt="⏹️ ENVIAR", key='speech')

    if texto_voz:
        prompt = f"Eres Pediatra. Jeferson dice: '{texto_voz}'. Responde breve con el manual: {st.session_state.pdf_text}"
        respuesta = model.generate_content(prompt)
        
        # Audio de respuesta y texto de apoyo
        st.info(f"Doctor: {respuesta.text}")
        audio_res = f"https://translate.google.com/translate_tts?ie=UTF-8&q={respuesta.text[:200]}&tl=es&client=tw-ob"
        st.audio(audio_res, format="audio/mp3", autoplay=True)

    if st.sidebar.button("Reiniciar"):
        st.session_state.clear()
        st.rerun()
