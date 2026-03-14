import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

st.set_page_config(page_title="Simulador Médico", layout="centered", page_icon="🩺")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "entrenado" not in st.session_state:
    st.session_state.entrenado = False
if "modelo_nombre" not in st.session_state:
    st.session_state.modelo_nombre = None

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
        
        # --- AUTO-DETECCIÓN DE MODELO ---
        if not st.session_state.modelo_nombre:
            modelos_disponibles = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            if modelos_disponibles:
                # Priorizamos flash si existe, si no, el primero disponible
                flash_models = [m for m in modelos_disponibles if 'flash' in m.lower()]
                st.session_state.modelo_nombre = flash_models[0] if flash_models else modelos_disponibles[0]
                st.success(f"Conectado con éxito al modelo: {st.session_state.modelo_nombre}")
            else:
                st.error("No se encontraron modelos disponibles en esta API Key.")

        if st.session_state.modelo_nombre:
            model = genai.GenerativeModel(st.session_state.modelo_nombre)

            archivo_guia = st.file_uploader("Sube el manual (PDF)", type="pdf")

            if archivo_guia and not st.session_state.entrenado:
                with st.spinner("El médico está leyendo..."):
                    reader = PdfReader(archivo_guia)
                    texto = "".join([page.extract_text() for page in reader.pages])
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
        st.error(f"Error técnico: {e}")
else:
    st.warning("Ingresa tu API Key.")
