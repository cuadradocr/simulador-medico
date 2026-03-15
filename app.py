import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
from streamlit_mic_recorder import speech_to_text

st.set_page_config(page_title="Simulador Voz: Jeferson", layout="centered")

# 1. Configuración de API
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.error("⚠️ Revisa la GEMINI_API_KEY en Secrets.")
    st.stop()

# 2. SISTEMA ANTIBLOQUEO: Busca el modelo disponible automáticamente
if "modelo_nombre" not in st.session_state:
    try:
        # Esto busca qué modelos tienes permitidos usar
        modelos_permitidos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # Intentamos usar flash, y si no, el primero que aparezca
        st.session_state.modelo_nombre = next((m for m in modelos_permitidos if '1.5-flash' in m), modelos_permitidos[0])
    except:
        # Si todo falla, usamos el nombre estándar manual
        st.session_state.modelo_nombre = "models/gemini-1.5-flash"

model = genai.GenerativeModel(st.session_state.modelo_nombre)

if "entrenado" not in st.session_state:
    st.session_state.entrenado = False

st.title("🎙️ Entrenamiento de Voz")

# 3. Carga del Manual
if not st.session_state.entrenado:
    archivo = st.file_uploader("Sube el PDF de Filinar G", type="pdf")
    if archivo:
        reader = PdfReader(archivo)
        st.session_state.pdf_text = "".join([p.extract_text() for p in reader.pages])[:8000]
        
        try:
            res = model.generate_content("Eres un Pediatra. Saluda a Jeferson Cuadrado de forma breve.")
            st.session_state.entrenado = True
            
            # AUDIO AUTOMÁTICO
            t_saludo = res.text.replace('*', '')
            audio_url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={t_saludo[:200]}&tl=es&client=tw-ob"
            st.audio(audio_url, format="audio/mp3", autoplay=True)
            st.rerun()
        except Exception as e:
            st.error(f"Error de conexión: {e}")

# 4. Interacción por Voz
if st.session_state.entrenado:
    st.markdown("### 👨‍⚕️ El Doctor te escucha...")
    
    # Botón de micrófono
    texto_voz = speech_to_text(language='es', start_prompt="🎤 TOCAR PARA HABLAR", stop_prompt="⏹️ ENVIAR", key='speech')

    if texto_voz:
        prompt = f"Eres Pediatra. Jeferson dice: '{texto_voz}'. Responde breve con el manual: {st.session_state.pdf_text}"
        respuesta = model.generate_content(prompt)
        
        # Audio de respuesta
        t_res = respuesta.text.replace('*', '')
        audio_res = f"https://translate.google.com/translate_tts?ie=UTF-8&q={t_res[:200]}&tl=es&client=tw-ob"
        
        st.info(f"Doctor dice: {respuesta.text}")
        st.audio(audio_res, format="audio/mp3", autoplay=True)
