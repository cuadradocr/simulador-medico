import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

# Configuración de interfaz limpia
st.set_page_config(page_title="Simulador de Voz Real", layout="centered", page_icon="🎙️")

# Intentar obtener la API KEY desde los secretos
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except:
    st.error("⚠️ No se encontró la API KEY en los secretos de Streamlit.")
    st.stop()

# Inicialización de estados
if "messages" not in st.session_state:
    st.session_state.messages = []
if "entrenado" not in st.session_state:
    st.session_state.entrenado = False
if "contador" not in st.session_state:
    st.session_state.contador = 0
if "modelo_nombre" not in st.session_state:
    st.session_state.modelo_nombre = None

st.title("🎙️ Entrenamiento de Voz: Jeferson Cuadrado")
st.markdown("---")

with st.sidebar:
    st.header("Estado de la Visita")
    st.info(f"Interacción: {st.session_state.contador} / 10")
    st.write("**Visitador:** Jeferson Cuadrado")
    if st.button("🔄 Reiniciar Sesión"):
        st.session_state.clear()
        st.rerun()

# Configuración del modelo
genai.configure(api_key=api_key)

if not st.session_state.modelo_nombre:
    try:
        modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        st.session_state.modelo_nombre = next((m for m in modelos if 'flash' in m.lower()), modelos[0])
    except:
        st.error("Error al conectar con los modelos de Google.")
        st.stop()

model = genai.GenerativeModel(st.session_state.modelo_nombre)

# Lógica de carga de Manual
if not st.session_state.entrenado:
    archivo = st.file_uploader("Sube el manual para que el doctor lo tenga de referencia", type="pdf")
    if archivo:
        with st.spinner("El Pediatra está alistando el consultorio..."):
            reader = PdfReader(archivo)
            texto = "".join([p.extract_text() for p in reader.pages])
            st.session_state.contexto_producto = texto
            
            prompt_inicial = (
                f"Eres un Pediatra real en una charla fluida con Jeferson Cuadrado. "
                f"Usa este manual solo para validar datos: {st.session_state.contexto_producto}. "
                "Tus respuestas deben ser cortas, naturales y conversacionales. "
                "Saluda a Jeferson para empezar la visita."
            )
            res = model.generate_content(prompt_inicial)
            st.session_state.messages.append({"role": "assistant", "content": res.text})
            st.session_state.entrenado = True
            
            # Audio del saludo inicial
            t_voz = res.text.replace('*', '').replace('#', '')
            st.audio(f"https://translate.google.com/translate_tts?ie=UTF-8&q={t_voz[:200]}&tl=es&client=tw-ob", autoplay=True)
            st.rerun()

# Interfaz de charla
if st.session_state.entrenado:
    # Mostramos el historial de forma simplificada
    for m in st.session_state.messages[-1:]: # Solo mostramos la última interacción para enfoque
        if m["role"] == "assistant":
            st.markdown("### 👨‍⚕️ El Doctor dice:")
            st.write(m["content"])

    if prompt := st.chat_input("Presiona el micrófono de tu teclado y presenta el producto..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.contador += 1
        
        # Evaluar reinicio
        if st.session_state.contador > 10:
            st.warning("Sesión terminada. ¡Buen trabajo, Jeferson!")
            st.stop()

        # Respuesta del doctor
        historial = f"Eres Pediatra en charla con Jeferson. Manual de apoyo: {st.session_state.contexto_producto}\n"
        for m in st.session_state.messages[-3:]:
            historial += f"{m['role']}: {m['content']}\n"
        
        respuesta = model.generate_content(historial)
        st.session_state.messages.append({"role": "assistant", "content": respuesta.text})
        
        # Generar audio automático
        t_voz = respuesta.text.replace('*', '').replace('#', '')
        st.audio(f"https://translate.google.com/translate_tts?ie=UTF-8&q={t_voz[:200]}&tl=es&client=tw-ob", autoplay=True)
        st.rerun()

 
