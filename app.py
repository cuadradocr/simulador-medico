import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

st.set_page_config(page_title="Simulador Pediatra", layout="centered", page_icon="👶")

# Estados de memoria
if "messages" not in st.session_state:
    st.session_state.messages = []
if "entrenado" not in st.session_state:
    st.session_state.entrenado = False
if "contador" not in st.session_state:
    st.session_state.contador = 0
if "modelo_nombre" not in st.session_state:
    st.session_state.modelo_nombre = None

st.title("🩺 Práctica Científica: Jeferson Cuadrado")

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
        
        # Auto-detección de modelo
        if not st.session_state.modelo_nombre:
            modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            st.session_state.modelo_nombre = next((m for m in modelos if 'flash' in m.lower()), modelos[0])

        if st.session_state.modelo_nombre:
            model = genai.GenerativeModel(st.session_state.modelo_nombre)
            archivo_guia = st.file_uploader("Carga el manual para que la IA verifique tus respuestas (PDF)", type="pdf")

            if archivo_guia and not st.session_state.entrenado:
                with st.spinner("Preparando consultorio..."):
                    reader = PdfReader(archivo_guia)
                    st.session_state.contexto_producto = "".join([p.extract_text() for p in reader.pages])[:15000]
                    
                    # PROMPT CORREGIDO: El médico NO sabe el producto, lo sabe JEFERSON.
                    prompt_sistema = (
                        f"Eres un Pediatra en su consultorio. Recibes a Jeferson Cuadrado. "
                        f"REGLA DE ORO: Tú NO conoces los beneficios de Filinar G todavía. Jeferson debe explicártelos. "
                        f"Usa este manual SOLAMENTE para verificar si Jeferson dice la verdad: {st.session_state.contexto_producto}. "
                        "Si Jeferson te da un dato científico, compáralo con el manual. Si es correcto, asiente. Si es falso o incompleto, cuestiónalo duramente. "
                        "Saluda a Jeferson y pregúntale qué producto nuevo trae hoy."
                    )
                    res = model.generate_content(prompt_sistema)
                    st.session_state.messages.append({"role": "assistant", "content": res.text})
                    st.session_state.entrenado = True
                    st.rerun()

            if st.session_state.contador >= 10:
                st.warning("Sesión completada. Evaluando desempeño...")
                # Aquí podrías añadir una lógica de evaluación final
                st.session_state.messages = []
                st.session_state.contador = 0
                st.session_state.entrenado = False
                st.rerun()

            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])

            if prompt := st.chat_input("Explica el mecanismo de acción o beneficios..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.session_state.contador += 1
                
                contexto_rol = (
                    f"Eres el Pediatra. Jeferson Cuadrado te está presentando un producto. "
                    f"Verifica sus afirmaciones con este manual: {st.session_state.contexto_producto}. "
                    "Si te convence con ciencia, interésate. Si no, sé escéptico."
                )
                
                # Construir historial para la IA
                historial_conversacion = contexto_rol + "\n"
                for m in st.session_state.messages:
                    historial_conversacion += f"{m['role']}: {m['content']}\n"
                
                respuesta = model.generate_content(historial_conversacion)
                st.session_state.messages.append({"role": "assistant", "content": respuesta.text})
                
                # Voz de salida
                t_voz = respuesta.text.replace('*', '').replace('#', '')
                st.audio(f"https://translate.google.com/translate_tts?ie=UTF-8&q={t_voz[:200]}&tl=es&client=tw-ob", autoplay=True)
                st.rerun()

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.warning("Ingresa tu API Key.")
