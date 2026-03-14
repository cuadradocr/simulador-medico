import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
from streamlit_mic_recorder import speech_to_text

# Configuración de página minimalista para evitar distracciones
st.set_page_config(page_title="Visita Médica: Jeferson", layout="centered")

# 1. Cargar API Key (Asegúrate de tenerla en Secrets)
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error("⚠️ Falta la API KEY en los Secrets de Streamlit.")
    st.stop()

# Inicialización de la sesión
if "messages" not in st.session_state:
    st.session_state.messages = []
if "entrenado" not in st.session_state:
    st.session_state.entrenado = False
if "contador" not in st.session_state:
    st.session_state.contador = 0

st.title("🎙️ Visita Médica: Jeferson Cuadrado")

# Usamos gemini-1.5-flash: es el más rápido y estable para voz
model = genai.GenerativeModel('gemini-1.5-flash')

# Paso 1: Carga del Manual de Filinar G
if not st.session_state.entrenado:
    archivo = st.file_uploader("Sube el PDF para que el Dr. lo analice", type="pdf")
    if archivo:
        with st.spinner("El Doctor está revisando el material..."):
            reader = PdfReader(archivo)
            # Tomamos una parte sustancial pero segura para no saturar la IA
            st.session_state.pdf_text = "".join([p.extract_text() for p in reader.pages])[:10000]
            
            prompt_saludo = (
                f"Eres un Pediatra amable. Saluda a Jeferson Cuadrado de forma muy breve. "
                f"Usa este manual como referencia científica: {st.session_state.pdf_text}"
            )
            res = model.generate_content(prompt_saludo)
            st.session_state.messages.append({"role": "assistant", "content": res.text})
            st.session_state.entrenado = True
            
            # Audio del saludo inicial
            t_voz = res.text.replace('*', '')
            st.audio(f"https://translate.google.com/translate_tts?ie=UTF-8&q={t_voz[:200]}&tl=es&client=tw-ob", autoplay=True)
            st.rerun()

# Paso 2: Interacción por Voz (Audífonos)
if st.session_state.entrenado:
    st.markdown("### 👨‍⚕️ El Doctor te está escuchando...")
    st.write(f"Interacción: {st.session_state.contador} / 10")
    
    # Botón de micrófono nativo (Speech to Text)
    # Al terminar de hablar, el texto se envía automáticamente
    texto_voz = speech_to_text(
        language='es',
        start_prompt="🎤 TOCAR PARA HABLAR (Usa tus audífonos)",
        stop_prompt="⏹️ ENVIAR AL DOCTOR",
        key='speech'
    )

    if texto_voz:
        st.session_state.contador += 1
        
        # El doctor responde basándose en el manual y lo que dijiste
        historial = (
            f"Eres el Pediatra. Jeferson dice: '{texto_voz}'. "
            f"Responde de forma natural y breve basándote en el manual: {st.session_state.pdf_text}"
        )
        
        try:
            with st.spinner("El Dr. está respondiendo..."):
                respuesta = model.generate_content(historial)
                st.session_state.messages.append({"role": "assistant", "content": respuesta.text})
                
                # Audio de respuesta del médico
                t_voz_res = respuesta.text.replace('*', '')
                st.audio(f"https://translate.google.com/translate_tts?ie=UTF-8&q={t_voz_res[:200]}&tl=es&client=tw-ob", autoplay=True)
                
                # Opcional: mostrar lo que dijo el doctor por si no se escuchó bien
                st.info(f"Doctor: {respuesta.text}")
        except Exception as e:
            st.error("El doctor se distrajo un momento (Error de conexión). Espera 10 segundos e intenta de nuevo.")

    if st.sidebar.button("🗑️ Reiniciar Sesión"):
        st.session_state.clear()
        st.rerun()
