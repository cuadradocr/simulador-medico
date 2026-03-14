import streamlit as st
import google.generativeai as genai
import os

# Configuración visual
st.set_page_config(page_title="Simulador de Visita Médica", layout="centered")
st.title("🩺 Mi Simulador de Visita")

# 1. Configurar la API Key (La pondremos en una caja de texto o secreta)
api_key = st.sidebar.text_input("Pega tu API Key de Google aquí", type="password")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    # 2. Subir las guías del producto
    archivo_guia = st.file_uploader("Sube la Guía del Producto (PDF)", type="pdf")

    if archivo_guia:
        # Iniciamos el chat si no existe
        if "chat" not in st.session_state:
            st.session_state.chat = model.start_chat(history=[])
            # Instrucción de Rol
            st.session_state.chat.send_message(
                f"Actúa como un médico. He subido una guía de producto. "
                f"Tu conocimiento se basa en este archivo. Sé realista, haz preguntas difíciles "
                f"y evalúa si el visitador conoce bien el producto. Empieza saludando."
            )

        # Mostrar historial de conversación
        for mensaje in st.session_state.chat.history:
            role = "Médico" if mensaje.role == "model" else "Tú"
            st.write(f"**{role}:** {mensaje.parts[0].text}")

        # 3. Entrada de voz/texto
        # En el celular, al tocar esta caja, se abre el teclado y puedes usar el micrófono.
        prompt = st.chat_input("Cuéntame sobre el producto...")
        
        if prompt:
            respuesta = st.session_state.chat.send_message(prompt)
            st.rerun() # Refresca para mostrar la respuesta
else:
    st.warning("Por favor, ingresa tu API Key en la barra lateral para comenzar.")
