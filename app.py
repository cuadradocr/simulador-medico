import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

st.set_page_config(page_title="Visita Médica Real", layout="centered", page_icon="🤝")

# Inicialización de estados
if "messages" not in st.session_state:
    st.session_state.messages = []
if "entrenado" not in st.session_state:
    st.session_state.entrenado = False
if "contador" not in st.session_state:
    st.session_state.contador = 0
if "modelo_nombre" not in st.session_state:
    st.session_state.modelo_nombre = None

st.title("🤝 Visita Médica: Jeferson Cuadrado")

with st.sidebar:
    st.header("Panel de Control")
    st.write(f"**Visitador:** Jeferson")
    st.write(f"**Charla:** {st.session_state.contador} / 10")
    st.divider()
    api_key = st.text_input("Pega tu API Key", type="password")
    if st.button("🗑️ Nueva Visita (Reset)"):
        st.session_state.clear()
        st.rerun()

if api_key:
    try:
        genai.configure(api_key=api_key)
        
        if not st.session_state.modelo_nombre:
            modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            st.session_state.modelo_nombre = next((m for m in modelos if 'flash' in m.lower()), modelos[0])

        if st.session_state.modelo_nombre:
            model = genai.GenerativeModel(st.session_state.modelo_nombre)
            archivo_guia = st.file_uploader("Sube el manual para que el doctor tenga sus apuntes (PDF)", type="pdf")

            if archivo_guia and not st.session_state.entrenado:
                with st.spinner("El Dr. se está acomodando en el consultorio..."):
                    reader = PdfReader(archivo_guia)
                    texto_completo = ""
                    for page in reader.pages:
                        content = page.extract_text()
                        if content: texto_completo += content + "\n"
                    
                    st.session_state.contexto_producto = texto_completo
                    
                    # PROMPT PARA CHARLA NATURAL
                    prompt_sistema = (
                        f"Actúa como un Pediatra amable y profesional. Jeferson Cuadrado es un visitador médico que ya conoces de antes. "
                        f"REGLA: No seas un robot. Habla de forma natural ('charladita'), usa frases como '¿Cómo va todo?', 'Cuéntame qué traes', 'Ese nombre me suena'. "
                        f"Aunque no conoces a fondo el producto Filinar G, usa este manual como si fuera una guía que tienes en tu escritorio para validar lo que Jeferson te dice: {st.session_state.contexto_producto}. "
                        "Si Jeferson te convence con buenos argumentos, muéstrate abierto. Si suena muy vendedor y poco científico, dile 'A ver, explícame eso mejor porque no me suena'. "
                        "Comienza saludando a Jeferson como si estuviera entrando a tu oficina en un día ocupado."
                    )
                    res = model.generate_content(prompt_sistema)
                    st.session_state.messages.append({"role": "assistant", "content": res.text})
                    st.session_state.entrenado = True
                    st.rerun()

            if st.session_state.contador >= 10:
                st.info("Bueno Jeferson, ya tengo que ver a otro paciente. ¡Hablamos luego!")
                if st.button("Empezar otra visita"):
                    st.session_state.clear()
                    st.rerun()
                st.stop()

            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])

            if prompt := st.chat_input("Dile algo al doctor..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.session_state.contador += 1
                
                # Contexto de charla real
                historial = f"Eres el Pediatra. Estás en una charla fluida con Jeferson. Manual de referencia: {st.session_state.contexto_producto}\n"
                for m in st.session_state.messages:
                    historial += f"{m['role']}: {m['content']}\n"
                
                respuesta = model.generate_content(historial)
                st.session_state.messages.append({"role": "assistant", "content": respuesta.text})
                
                # Audio para que la charla sea real
                t_voz = respuesta.text.replace('*', '').replace('#', '')
                st.audio(f"https://translate.google.com/translate_tts?ie=UTF-8&q={t_voz[:200]}&tl=es&client=tw-ob", autoplay=True)
                st.rerun()

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.warning("Ingresa tu API Key.")

 
