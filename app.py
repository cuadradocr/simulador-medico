import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
from streamlit_mic_recorder import speech_to_text

st.set_page_config(page_title="Simulador Voz: Jeferson", layout="centered")

# 1. Conexión con Secrets
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.error("⚠️ Error: Configura la GEMINI_API_KEY en Secrets.")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "entrenado" not in st.session_state:
    st.session_state.entrenado = False

st.title("🎙️ Visita Médica: Jeferson Cuadrado")

# 2. Modelo Flash (El más rápido para evitar bloqueos)
model = genai.GenerativeModel('gemini-1.5-flash')

# 3. Carga del Manual (Optimizado)
if not st.session_state.entrenado:
    archivo = st.file_uploader("Sube el PDF de Filinar G", type="pdf")
    if archivo:
        with st.spinner("El Doctor está analizando el material..."):
            reader = PdfReader(archivo)
            # Solo enviamos las partes clave para no saturar la memoria
            st.session_state.pdf_text = "".join([p.extract_text() for p in reader.pages])[:8000]
            
            res = model.generate_content("Eres un Pediatra. Saluda a Jeferson Cuadrado de forma breve y amable.")
            st.session_state.messages.append({"role": "assistant", "content": res.text})
            st.session_state.entrenado = True
            
            # Audio automático de saludo
            st.audio(f"https://translate.google.com/translate_tts?ie=UTF-8&q={res.text[:200]}&tl=es&client=tw-ob", autoplay=True)
            st.rerun()

# 4. Interacción por Voz (Audífonos)
if st.session_state.entrenado:
    st.markdown("### 👨‍⚕️ El Doctor te está escuchando...")
    
    # Este botón activará tus audífonos
    texto_voz = speech_to_text(
        language='es',
        start_prompt="🎤 TOCAR PARA HABLAR",
        stop_prompt="⏹️ ENVIAR AL DOCTOR",
        key='speech'
    )

    if texto_voz:
        # El doctor responde usando el manual pero de forma resumida
        historial = f"Eres Pediatra. Jeferson dice: '{texto_voz}'. Responde brevemente con base en este manual: {st.session_state.pdf_text}"
        
        try:
            respuesta = model.generate_content(historial)
            st.session_state.messages.append({"role": "assistant", "content": respuesta.text})
            
            # Voz del doctor
            t_voz = respuesta.text.replace('*', '')
            st.audio(f"https://translate.google.com/translate_tts?ie=UTF-8&q={t_voz[:200]}&tl=es&client=tw-ob", autoplay=True)
            
            # Mostramos el texto por si hay ruido ambiente
            st.info(f"Doctor: {respuesta.text}")
        except:
            st.error("El doctor se saturó. Espera 5 segundos y vuelve a intentar.")

    if st.sidebar.button("🗑️ Reiniciar Sesión"):
        st.session_state.clear()
        st.rerun()
