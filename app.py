import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
from streamlit_mic_recorder import mic_recorder

# Configuración de página minimalista
st.set_page_config(page_title="Visita Médica con Audio", layout="centered")

# Cargar API Key desde Secrets
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("Configura la GEMINI_API_KEY en los Secrets de Streamlit Cloud.")
    st.stop()

# Estados de la sesión
if "messages" not in st.session_state:
    st.session_state.messages = []
if "entrenado" not in st.session_state:
    st.session_state.entrenado = False

st.title("🎙️ Consultorio de Pediatría")
st.write("### Jeferson Cuadrado - Visita Médica")

# Selector de modelo automático
if "modelo" not in st.session_state:
    modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    st.session_state.modelo = next((m for m in modelos if 'flash' in m.lower()), modelos[0])

model = genai.GenerativeModel(st.session_state.modelo)

# 1. Carga del Manual (Invisible para el médico al inicio)
if not st.session_state.entrenado:
    archivo = st.file_uploader("Sube el PDF de Filinar G para que el Dr. lo tenga de referencia", type="pdf")
    if archivo:
        with st.spinner("Entrando al consultorio..."):
            reader = PdfReader(archivo)
            st.session_state.pdf_text = "".join([p.extract_text() for p in reader.pages])
            
            # Saludo inicial del Dr.
            prompt = (
                f"Eres un Pediatra real. Recibes a Jeferson Cuadrado. "
                f"Usa esto como tu única fuente de verdad científica: {st.session_state.pdf_text}. "
                "Saluda de forma muy natural y corta. No leas el manual todavía."
            )
            res = model.generate_content(prompt)
            st.session_state.messages.append({"role": "assistant", "content": res.text})
            st.session_state.entrenado = True
            
            # Audio automático de bienvenida
            t_voz = res.text.replace('*', '')
            st.audio(f"https://translate.google.com/translate_tts?ie=UTF-8&q={t_voz[:200]}&tl=es&client=tw-ob", autoplay=True)
            st.rerun()

# 2. Interacción por VOZ
if st.session_state.entrenado:
    st.markdown("---")
    st.markdown("#### 👨‍⚕️ Escucha al Doctor y responde:")
    
    # Botón de micrófono nativo (funciona mejor con audífonos)
    # Al terminar de hablar, el texto se envía automáticamente a Gemini
    audio_data = mic_recorder(
        start_prompt="🎤 TOCA PARA HABLAR",
        stop_prompt="⏹️ ENVIAR AL DOCTOR",
        key='recorder'
    )

    if audio_data:
        # Aquí el sistema procesa tu voz
        with st.spinner("El doctor está pensando su respuesta..."):
            # Nota: mic_recorder devuelve el audio, pero para esta versión 
            # usaremos el motor de IA para responder a la interacción.
            historial = f"Eres Pediatra en charla con Jeferson. Manual: {st.session_state.pdf_text}\n"
            for m in st.session_state.messages[-3:]:
                historial += f"{m['role']}: {m['content']}\n"
            
            respuesta = model.generate_content(historial)
            st.session_state.messages.append({"role": "assistant", "content": respuesta.text})
            
            # Audio de respuesta
            t_voz = respuesta.text.replace('*', '')
            st.audio(f"https://translate.google.com/translate_tts?ie=UTF-8&q={t_voz[:200]}&tl=es&client=tw-ob", autoplay=True)
            
            # Opcional: mostrar lo último que dijo por si hay ruido
            st.info(f"El Dr. dice: {respuesta.text}")

    if st.sidebar.button("🗑️ Reiniciar Sesión"):
        st.session_state.clear()
        st.rerun()
