import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
from streamlit_mic_recorder import speech_to_text

st.set_page_config(page_title="Simulador de Voz: Jeferson", layout="centered")

# 1. Conexión Segura
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.error("⚠️ Configura la GEMINI_API_KEY en los Secrets de Streamlit.")
    st.stop()

# Inicializar estados
if "messages" not in st.session_state:
    st.session_state.messages = []
if "entrenado" not in st.session_state:
    st.session_state.entrenado = False

st.title("🎙️ Visita Médica: Solo Voz")

# 2. ELIMINADOR DE ERROR 404 (Busca el modelo disponible automáticamente)
if "modelo_nombre" not in st.session_state:
    try:
        # Buscamos qué modelos tienes permitidos
        modelos_disponibles = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # Preferimos el 1.5-flash porque es el mejor para voz y es rápido
        st.session_state.modelo_nombre = next((m for m in modelos_disponibles if '1.5-flash' in m), modelos_disponibles[0])
    except:
        st.session_state.modelo_nombre = "models/gemini-1.5-flash"

model = genai.GenerativeModel(st.session_state.modelo_nombre)

# 3. Carga del Manual de Filinar G
if not st.session_state.entrenado:
    archivo = st.file_uploader("Sube el PDF para que el Dr. lo analice", type="pdf")
    if archivo:
        with st.spinner("El Doctor está entrando al consultorio..."):
            reader = PdfReader(archivo)
            # Guardamos el texto del manual (limitado para no saturar)
            st.session_state.pdf_text = "".join([p.extract_text() for p in reader.pages])[:8000]
            
            # Saludo inicial
            res = model.generate_content("Eres un Pediatra amable. Saluda a Jeferson Cuadrado de forma muy breve.")
            st.session_state.entrenado = True
            
            # VOZ AUTOMÁTICA (Primera vez)
            st.audio(f"https://translate.google.com/translate_tts?ie=UTF-8&q={res.text[:200]}&tl=es&client=tw-ob", autoplay=True)
            st.rerun()

# 4. INTERACCIÓN POR VOZ (Audífonos)
if st.session_state.entrenado:
    st.markdown("### 👨‍⚕️ El Doctor te escucha...")
    
    # Botón de micrófono nativo (Speech to Text)
    texto_voz = speech_to_text(
        language='es',
        start_prompt="🎤 TOCA PARA HABLAR",
        stop_prompt="⏹️ ENVIAR AL DOCTOR",
        key='speech'
    )

    if texto_voz:
        # El doctor responde basándose en el manual y tu voz
        contexto = f"Eres Pediatra. Jeferson dice: '{texto_voz}'. Responde breve usando el manual: {st.session_state.pdf_text}"
        respuesta = model.generate_content(contexto)
        
        # Audio de respuesta del médico
        t_voz = respuesta.text.replace('*', '') # Limpiamos símbolos
        st.audio(f"https://translate.google.com/translate_tts?ie=UTF-8&q={t_voz[:200]}&tl=es&client=tw-ob", autoplay=True)
        
        # Solo mostramos un aviso para que sepas que respondió
        st.info("Doctor respondió (Escucha tus audífonos)")

    if st.sidebar.button("🗑️ Reiniciar Sesión"):
        st.session_state.clear()
        st.rerun()
