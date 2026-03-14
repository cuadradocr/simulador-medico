import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

st.set_page_config(page_title="Simulador Médico Pro", layout="centered")
st.title("🩺 Simulador: Visita Médica")

# Sidebar para configuración
with st.sidebar:
    api_key = st.text_input("Pega tu API Key de Google", type="password")
    st.info("Configura tu clave para empezar.")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    # Subida de archivo
    archivo_guia = st.file_uploader("Sube el manual del producto (PDF)", type="pdf")

    if archivo_guia:
        # LEER EL PDF
        @st.cache_data # Para que no lea el PDF cada vez que hablas
        def extraer_texto(pdf):
            reader = PdfReader(pdf)
            texto = ""
            for page in reader.pages:
                texto += page.extract_text()
            return texto

        texto_pdf = extraer_texto(archivo_guia)

        # Iniciar Chat
        if "chat" not in st.session_state:
            st.session_state.chat = model.start_chat(history=[])
            # El "Prompt" de sistema con el contenido del PDF
            instruccion = (
                f"Eres un médico especialista. He recibido este manual de producto: {texto_pdf}. "
                "Tu objetivo es actuar como un médico en su consultorio. Sé profesional, algo ocupado "
                "y evalúa rigurosamente lo que el visitador te diga basado en el manual. "
                "No menciones que eres una IA ni que leíste un PDF. Saluda brevemente para empezar."
            )
            st.session_state.chat.send_message(instruccion)

        # Mostrar conversación
        for mensaje in st.session_state.chat.history[1:]: # Saltamos la instrucción secreta
            role = "Médico" if mensaje.role == "model" else "Tú"
            with st.chat_message(mensaje.role):
                st.write(f"**{role}:** {mensaje.parts[0].text}")

        # Entrada de usuario
        prompt = st.chat_input("Escribe o usa el micrófono del cel...")
        if prompt:
            st.session_state.chat.send_message(prompt)
            st.rerun()
else:
    st.warning("Falta la API Key en la barra lateral.")
