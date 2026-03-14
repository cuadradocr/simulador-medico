import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

st.set_page_config(page_title="Simulador Pediatra", layout="centered", page_icon="👶")

# Inicialización de estados de memoria
if "messages" not in st.session_state:
    st.session_state.messages = []
if "entrenado" not in st.session_state:
    st.session_state.entrenado = False
if "contador" not in st.session_state:
    st.session_state.contador = 0
if "modelo_nombre" not in st.session_state:
    st.session_state.modelo_nombre = None

st.title("🩺 Sesión de Rol-Play: Pediatría")

with st.sidebar:
    st.header("Perfil")
    st.write(f"**Visitador:** Jeferson Cuadrado")
    st.write(f"**Interacciones:** {st.session_state.contador} / 10")
    st.divider()
    api_key = st.text_input("Pega tu API Key", type="password")
    if st.button("🗑️ Reiniciar Manualmente"):
        st.session_state.clear()
        st.rerun()

if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # --- AUTO-DETECCIÓN DE MODELO PARA EVITAR ERROR 404 ---
        if not st.session_state.modelo_nombre:
            modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            if modelos:
                # Priorizamos gemini-1.5-flash si existe
                flash = [m for m in modelos if 'flash' in m.lower()]
                st.session_state.modelo_nombre = flash[0] if flash else modelos[0]
            else:
                st.error("No hay modelos disponibles en esta Key.")

        if st.session_state.modelo_nombre:
            model = genai.GenerativeModel(st.session_state.modelo_nombre)
            archivo_guia = st.file_uploader("Sube el manual de Filinar G (PDF)", type="pdf")

            if archivo_guia and not st.session_state.entrenado:
                with st.spinner("El Pediatra está leyendo el manual..."):
                    reader = PdfReader(archivo_guia)
                    texto = "".join([page.extract_text() for page in reader.pages])
                    st.session_state.contexto_producto = texto[:12000]
                    
                    prompt_pediatra = (
                        f"Eres un Pediatra experto. Recibes a Jeferson Cuadrado. "
                        f"Tu conocimiento de Filinar G es: {st.session_state.contexto_producto}. "
                        "Eres profesional, te preocupa la seguridad infantil. Saluda a Jeferson."
                    )
                    res = model.generate_content(prompt_pediatra)
                    st.session_state.messages.append({"role": "assistant", "content": res.text})
                    st.session_state.entrenado = True
                    st.rerun()

            # Reinicio automático a las 10 preguntas
            if st.session_state.contador >= 10:
                st.warning("Límite de 10 interacciones alcanzado. Reiniciando...")
                st.session_state.messages = []
                st.session_state.contador = 0
                st.session_state.entrenado = False
                st.rerun()

            # Mostrar chat
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])

            # Entrada de voz/texto
            if prompt := st.chat_input("Presenta el producto aquí..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.session_state.contador += 1
                
                # Construcción del contexto para la respuesta
                historial = f"Eres Pediatra. Visitador: Jeferson Cuadrado. Manual: {st.session_state.contexto_producto}\n"
                for m in st.session_state.messages:
                    historial += f"{m['role']}: {m['content']}\n"
                
                respuesta = model.generate_content(historial)
                st.session_state.messages.append({"role": "assistant", "content": respuesta.text})
                
                # Audio automático (Voz del médico)
                t_voz = respuesta.text.replace('*', '').replace('#', '')
                st.audio(f"https://translate.google.com/translate_tts?ie=UTF-8&q={t_voz[:200]}&tl=es&client=tw-ob", autoplay=True)
                st.rerun()

    except Exception as e:
        st.error(f"Error técnico: {e}")
else:
    st.warning("Ingresa tu API Key en la izquierda.")
