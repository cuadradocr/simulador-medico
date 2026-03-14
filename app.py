import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
from streamlit_mic_recorder import speech_to_text

st.set_page_config(page_title="Simulador de Voz", layout="centered", page_icon="🎙️")

# 1. Conectar con la llave oculta (Secrets)
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.error("⚠️ Error: Configura la GEMINI_API_KEY en los Secrets de Streamlit Cloud.")
    st.stop()

# Inicializar memoria
if "messages" not in st.session_state:
    st.session_state.messages = []
if "entrenado" not in st.session_state:
    st.session_state.entrenado = False

st.title("🎙️ Visita Médica: Jeferson Cuadrado")

# 2. Buscar el modelo disponible automáticamente (Evita el error 404)
if "modelo_ok" not in st.session_state:
    modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    st.session_state.modelo_ok = next((m for m in modelos if '1.5-flash' in m), modelos[0])

model = genai.GenerativeModel(st.session_state.modelo_ok)

# 3. Carga del Manual
if not st.session_state.entrenado:
    archivo = st.file_uploader("Sube el PDF de Filinar G para que el Dr. lo analice", type="pdf")
    if archivo:
        with st.spinner("El Doctor está entrando al consultorio..."):
            reader = PdfReader(archivo)
            st.session_state.pdf_text = "".join([p.extract_text() for p in reader.pages])
            
            prompt_saludo = f"Eres un Pediatra. Saluda a Jeferson Cuadrado. Manual de referencia: {st.session_state.pdf_text[:5000]}"
            res = model.generate_content(prompt_saludo)
            st.session_state.messages.append({"role": "assistant", "content": res.text})
            st.session_state.entrenado = True
            
            # Audio de saludo
            t_voz = res.text.replace('*', '')
            st.audio(f"https://translate.google.com/translate_tts?ie=UTF-8&q={t_voz[:200]}&tl=es&client=tw-ob", autoplay=True)
            st.rerun()

# 4. Interacción por Voz (Audífonos)
if st.session_state.entrenado:
    st.write("### 👨‍⚕️ El Doctor te está escuchando...")
    
    # Este botón captura tu voz y la envía al doctor
    texto_voz = speech_to_text(
        language='es',
        start_prompt="🎤 TOCAR PARA HABLAR (Usa tus audífonos)",
        stop_prompt="⏹️ ENVIAR AL DOCTOR",
        key='speech'
    )

    if texto_voz:
        st.session_state.messages.append({"role": "user", "content": texto_voz})
        
        # El doctor responde basado en el PDF y lo que tú dijiste
        historial = f"Eres Pediatra. Jeferson dice: {texto_voz}. Manual: {st.session_state.pdf_text[:5000]}"
        respuesta = model.generate_content(historial)
        st.session_state.messages.append({"role": "assistant", "content": respuesta.text})
        
        # Reproducir la voz del doctor
        t_voz_res = respuesta.text.replace('*', '')
        st.audio(f"https://translate.google.com/translate_tts?ie=UTF-8&q={t_voz_res[:200]}&tl=es&client=tw-ob", autoplay=True)
        st.rerun()
