import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

# Interfaz minimalista para enfoque total en audio
st.set_page_config(page_title="Simulador de Voz", layout="centered", page_icon="🎙️")

# 1. Obtener la API KEY de los secretos
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except:
    st.error("⚠️ Falta la API KEY en Secrets. Agrégala en la configuración de Streamlit Cloud.")
    st.stop()

# Inicialización de estados
if "messages" not in st.session_state:
    st.session_state.messages = []
if "entrenado" not in st.session_state:
    st.session_state.entrenado = False
if "contador" not in st.session_state:
    st.session_state.contador = 0

st.title("🎙️ Práctica de Voz: Jeferson Cuadrado")
st.markdown("---")

with st.sidebar:
    st.header("Info")
    st.write(f"**Turno:** {st.session_state.contador} / 10")
    if st.button("🔄 Nueva Visita"):
        st.session_state.clear()
        st.rerun()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# Carga de Manual (Solo una vez al inicio)
if not st.session_state.entrenado:
    archivo = st.file_uploader("Sube el manual para que el doctor pueda escucharte", type="pdf")
    if archivo:
        with st.spinner("Entrando al consultorio..."):
            reader = PdfReader(archivo)
            texto_pdf = "".join([p.extract_text() for p in reader.pages])
            st.session_state.contexto_producto = texto_pdf
            
            # Prompt para que sea puramente hablado y corto
            prompt_inicial = (
                f"Eres un Pediatra en una charla real con Jeferson Cuadrado. "
                f"Usa este manual solo para validar datos: {st.session_state.contexto_producto}. "
                "Responde de forma muy breve (máximo 2 frases) y muy natural. "
                "Saluda a Jeferson para empezar."
            )
            res = model.generate_content(prompt_inicial)
            st.session_state.messages.append({"role": "assistant", "content": res.text})
            st.session_state.entrenado = True
            
            # AUDIO DEL SALUDO
            t_voz = res.text.replace('*', '').replace('#', '')
            st.audio(f"https://translate.google.com/translate_tts?ie=UTF-8&q={t_voz[:200]}&tl=es&client=tw-ob", autoplay=True)
            st.rerun()

# 2. EL DOCTOR TE HABLA (Interfaz oculta)
if st.session_state.entrenado:
    # Mostramos un indicador visual en lugar del texto
    st.markdown("### 👨‍⚕️ El Pediatra te está escuchando...")
    st.write("*(Usa el micrófono de tu teclado para responderle)*")

    if prompt := st.chat_input("Di algo (Mecanismo, beneficios, etc)..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.contador += 1
        
        if st.session_state.contador > 10:
            st.warning("Sesión terminada. ¡Excelente práctica, Jeferson!")
            st.stop()

        # Respuesta del doctor con historial corto para rapidez
        historial = f"Eres Pediatra en charla con Jeferson. Manual: {st.session_state.contexto_producto}\n"
        for m in st.session_state.messages[-3:]:
            historial += f"{m['role']}: {m['content']}\n"
        
        respuesta = model.generate_content(historial)
        st.session_state.messages.append({"role": "assistant", "content": respuesta.text})
        
        # GENERAR Y REPRODUCIR AUDIO AUTOMÁTICAMENTE
        t_voz = respuesta.text.replace('*', '').replace('#', '')
        # Formateamos la URL para evitar errores con espacios
        url_audio = f"https://translate.google.com/translate_tts?ie=UTF-8&q={t_voz[:200]}&tl=es&client=tw-ob"
        
        st.audio(url_audio, format="audio/mp3", autoplay=True)
        # Opcional: mostrar el texto en pequeño o dejarlo oculto
        # st.write(respuesta.text) # Descomenta si quieres ver qué dijo en caso de no oír bien
        st.rerun()
