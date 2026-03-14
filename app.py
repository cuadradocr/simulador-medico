import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

# 1. Configuración de página - Debe ser lo primero
st.set_page_config(page_title="Simulador Médico", layout="centered", page_icon="🩺")

# 2. Inicialización de estados de memoria
if "messages" not in st.session_state:
    st.session_state.messages = []
if "entrenado" not in st.session_state:
    st.session_state.entrenado = False
if "contexto_producto" not in st.session_state:
    st.session_state.contexto_producto = ""

st.title("🩺 Simulador de Visita Médica")
st.markdown("### Practica tu speech de ventas con IA")

# Barra lateral
with st.sidebar:
    st.header("Configuración")
    api_key = st.text_input("Pega tu API Key de Google", type="password")
    
    st.divider()
    
    if st.button("🗑️ Reiniciar Todo / Nueva Visita"):
        st.session_state.clear()
        st.rerun()

# Lógica Principal
if api_key:
    try:
        genai.configure(api_key=api_key)
        # CAMBIO CLAVE: Nombre completo del modelo
        model = genai.GenerativeModel('models/gemini-1.5-flash')

        # Subida de archivo
        archivo_guia = st.file_uploader("Sube el manual de producto (PDF)", type="pdf")

        if archivo_guia and not st.session_state.entrenado:
            with st.spinner("El médico está revisando el material..."):
                # Leer PDF
                reader = PdfReader(archivo_guia)
                texto_extraido = ""
                for page in reader.pages:
                    texto_extraido += page.extract_text()
                
                st.session_state.contexto_producto = texto_extraido[:15000] # Guardamos hasta 15k caracteres
                
                # Prompt de sistema para iniciar la personalidad
                prompt_sistema = (
                    f"Actúa como un médico especialista. Conoces a fondo este producto: {st.session_state.contexto_producto}. "
                    "Instrucciones: Eres un médico en su consulta, eres profesional pero tienes poco tiempo. "
                    "Evalúa si el visitador médico conoce los beneficios y seguridad del producto. "
                    "Empieza la conversación saludando al visitador que entra a tu consultorio."
                )
                
                # Generar primer saludo
                res = model.generate_content(prompt_sistema)
                st.session_state.messages.append({"role": "assistant", "content": res.text})
                st.session_state.entrenado = True
                st.rerun()

        # Mostrar el historial del chat
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        # Entrada del usuario (Voz o Texto)
        if prompt := st.chat_input("Escribe o usa el micrófono de tu móvil..."):
            # Guardar y mostrar mensaje del usuario
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)

            # Construir la respuesta de la IA con el contexto
            with st.spinner("El médico está respondiendo..."):
                # Enviamos el contexto del PDF + la conversación actual
                contexto_y_chat = f"Contexto del Producto: {st.session_state.contexto_producto}\n\n"
                for m in st.session_state.messages:
                    contexto_y_chat += f"{m['role']}: {m['content']}\n"
                
                respuesta_ia = model.generate_content(contexto_y_chat)
                
                st.session_state.messages.append({"role": "assistant", "content": respuesta_ia.text})
                st.rerun()

    except Exception as e:
        st.error(f"Error de conexión o configuración: {e}")
        st.info("Asegúrate de que tu API Key sea válida y dale al botón 'Reiniciar Todo'.")
else:
    st.warning("👈 Por favor, ingresa tu API Key en la barra lateral para comenzar.")
