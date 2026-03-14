import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

# 1. Configuración de página al inicio
st.set_page_config(page_title="Simulador Médico", layout="centered")

# 2. Inicialización de estados para evitar errores de "NotFound"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "entrenado" not in st.session_state:
    st.session_state.entrenado = False

st.title("🩺 Simulador de Visita Médica")

# Barra lateral
with st.sidebar:
    api_key = st.text_input("Pega tu API Key de Google", type="password")
    if st.button("Reiniciar Todo"):
        st.session_state.clear()
        st.rerun()

if api_key:
    try:
        genai.configure(api_key=api_key)
        # Usamos gemini-1.5-flash que es el más rápido y estable para esto
        model = genai.GenerativeModel('gemini-1.5-flash')

        archivo_guia = st.file_uploader("Sube el manual (PDF)", type="pdf")

        if archivo_guia and not st.session_state.entrenado:
            with st.spinner("El médico está leyendo el manual..."):
                reader = PdfReader(archivo_guia)
                texto_pdf = ""
                for page in reader.pages:
                    texto_pdf += page.extract_text()
                
                # Guardamos el texto en la sesión para que no se pierda
                st.session_state.contexto_producto = texto_pdf[:10000] # Limite de 10k caracteres
                
                # Primer saludo del médico
                prompt_inicial = f"Eres un médico profesional. Conoces este producto: {st.session_state.contexto_producto}. Salúdame como si yo fuera un visitador médico que acaba de entrar a tu consultorio. Sé breve."
                res = model.generate_content(prompt_inicial)
                
                st.session_state.messages.append({"role": "assistant", "content": res.text})
                st.session_state.entrenado = True
                st.rerun()

        # Mostrar chat
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        # Entrada de usuario
        if prompt := st.chat_input("Escribe aquí..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)

            # Enviar contexto + historial a la IA
            contexto_completo = f"Contexto del producto: {st.session_state.get('contexto_producto', '')}\n\n"
            for m in st.session_state.messages:
                contexto_completo += f"{m['role']}: {m['content']}\n"
            
            respuesta = model.generate_content(contexto_completo)
            st.session_state.messages.append({"role": "assistant", "content": respuesta.text})
            st.rerun()

    except Exception as e:
        st.error(f"Hubo un problema de conexión: {e}")
        st.info("Prueba a darle al botón 'Reiniciar Todo' en la izquierda.")
else:
    st.warning("Ingresa tu API Key para comenzar.")
