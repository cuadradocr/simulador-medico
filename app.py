import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

st.set_page_config(page_title="Simulador Médico Pro", layout="centered")
st.title("🩺 Simulador: Visita Médica")

# Sidebar para configuración
with st.sidebar:
    api_key = st.text_input("Pega tu API Key de Google", type="password")
    if st.button("Reiniciar Conversación"):
        st.session_state.clear()
        st.rerun()

if api_key:
    genai.configure(api_key=api_key)
    
    # Subida de archivo
    archivo_guia = st.file_uploader("Sube el manual del producto (PDF)", type="pdf")

    if archivo_guia:
        # Extraer texto del PDF de forma segura
        reader = PdfReader(archivo_guia)
        texto_pdf = ""
        for page in reader.pages:
            texto_pdf += page.extract_text()
        
        # Configurar el modelo
        model = genai.GenerativeModel('gemini-1.5-flash')

        # Iniciar historial si no existe
        if "messages" not in st.session_state:
            st.session_state.messages = []
            # Enviamos la instrucción inicial de forma interna
            contexto = (
                f"Eres un médico especialista. Conoces este producto: {texto_pdf[:5000]}. "
                "Responde como un médico real en su consulta. Sé breve y profesional."
            )
            # El primer mensaje lo genera la IA para saludar
            res = model.generate_content(contexto + " Salúdame brevemente para empezar la visita.")
            st.session_state.messages.append({"role": "assistant", "content": res.text})

        # Mostrar los mensajes
        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(msg["content"])

        # Entrada de usuario
        if prompt := st.chat_input("Escribe tu mensaje aquí..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)
            
            # Generar respuesta basada en el historial
            # Limitamos el texto del PDF para no saturar la memoria
            historial_input = f"Contexto producto: {texto_pdf[:3000]}\n\n"
            for m in st.session_state.messages:
                historial_input += f"{m['role']}: {m['content']}\n"
            
            respuesta = model.generate_content(historial_input)
            st.session_state.messages.append({"role": "assistant", "content": respuesta.text})
            st.rerun()
else:
    st.warning("Falta la API Key en la barra lateral.")
