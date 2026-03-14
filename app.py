import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

st.set_page_config(page_title="Simulador Médico", layout="centered", page_icon="🩺")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "entrenado" not in st.session_state:
    st.session_state.entrenado = False
if "contexto_producto" not in st.session_state:
    st.session_state.contexto_producto = ""

st.title("🩺 Simulador de Visita Médica")

with st.sidebar:
    st.header("Configuración")
    api_key = st.text_input("Pega tu API Key de Google", type="password")
    if st.button("🗑️ Reiniciar Todo"):
        st.session_state.clear()
        st.rerun()

if api_key:
    try:
        genai.configure(api_key=api_key)
        # USAMOS GEMINI-PRO PARA MÁXIMA COMPATIBILIDAD
        model = genai.GenerativeModel('gemini-pro')

        archivo_guia = st.file_uploader("Sube el manual (PDF)", type="pdf")

        if archivo_guia and not st.session_state.entrenado:
            with st.spinner("El médico está leyendo..."):
                reader = PdfReader(archivo_guia)
                texto = ""
                for page in reader.pages:
                    texto += page.extract_text()
                st.session_state.contexto_producto = texto[:10000]
                
                res = model.generate_content(f"Eres un médico. Conoces este producto: {st.session_state.contexto_producto}. Saluda al visitador brevemente.")
                st.session_state.messages.append({"role": "assistant", "content": res.text})
                st.session_state.entrenado = True
                st.rerun()

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        if prompt := st.chat_input("Habla con el médico..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)

            contexto_total = f"Manual: {st.session_state.contexto_producto}\n\n"
            for m in st.session_state.messages:
                contexto_total += f"{m['role']}: {m['content']}\n"
            
            respuesta = model.generate_content(contexto_total)
            st.session_state.messages.append({"role": "assistant", "content": respuesta.text})
            st.rerun()

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.warning("Ingresa tu API Key.")
