import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

st.set_page_config(page_title="Simulador Pediatra", layout="centered", page_icon="👶")

# Inicialización de estados
if "messages" not in st.session_state:
    st.session_state.messages = []
if "entrenado" not in st.session_state:
    st.session_state.entrenado = False
if "contador" not in st.session_state:
    st.session_state.contador = 0

st.title("🩺 Sesión de Rol-Play: Pediatría")
st.sidebar.write(f"**Visitador:** Jeferson Cuadrado")
st.sidebar.write(f"**Interacciones:** {st.session_state.contador} / 10")

with st.sidebar:
    api_key = st.text_input("API Key", type="password")
    if st.button("Reiniciar Manualmente"):
        st.session_state.clear()
        st.rerun()

if api_key:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro') # O el que te funcionó antes

        archivo_guia = st.file_uploader("Sube el manual de Filinar G (PDF)", type="pdf")

        if archivo_guia and not st.session_state.entrenado:
            reader = PdfReader(archivo_guia)
            texto = "".join([page.extract_text() for page in reader.pages])
            st.session_state.contexto_producto = texto[:10000]
            
            # PROMPT PERSONALIZADO
            prompt_pediatra = (
                f"Eres un PEDIATRA experto. Estás recibiendo a JEFERSON CUADRADO, un visitador médico. "
                f"Conoces el producto Filinar G por este manual: {st.session_state.contexto_producto}. "
                "Tu tono es profesional, te preocupas mucho por la dosificación en niños y los efectos secundarios. "
                "Saluda a Jeferson por su nombre para comenzar la visita."
            )
            
            res = model.generate_content(prompt_pediatra)
            st.session_state.messages.append({"role": "assistant", "content": res.text})
            st.session_state.entrenado = True
            st.rerun()

        # Lógica de reinicio automático a las 10 preguntas
        if st.session_state.contador >= 10:
            st.warning("⚠️ Se ha alcanzado el límite de 10 interacciones. Reiniciando para una nueva práctica...")
            st.session_state.messages = []
            st.session_state.contador = 0
            st.session_state.entrenado = False
            st.rerun()

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        if prompt := st.chat_input("Habla con el Pediatra..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.session_state.contador += 1 # Aumenta el contador
            
            contexto_total = f"Manual: {st.session_state.contexto_producto}\n"
            contexto_total += f"Eres Pediatra. El visitador es Jeferson Cuadrado. Historial:\n"
            for m in st.session_state.messages:
                contexto_total += f"{m['role']}: {m['content']}\n"
            
            respuesta = model.generate_content(contexto_total)
            st.session_state.messages.append({"role": "assistant", "content": respuesta.text})
            
            # Audio automático
            texto_voz = respuesta.text.replace('*', '')
            st.audio(f"https://translate.google.com/translate_tts?ie=UTF-8&q={texto_voz[:200]}&tl=es&client=tw-ob", autoplay=True)
            
            st.rerun()

    except Exception as e:
        st.error(f"Error: {e}")
