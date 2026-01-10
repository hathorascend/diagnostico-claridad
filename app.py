import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import io
import pandas as pd
import google.generativeai as genai

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Hathora - Suite de Coaching Estratégico", layout="centered")

# --- INICIALIZACIÓN DE ESTADOS ---
if 'datos_rueda' not in st.session_state:
    st.session_state.datos_rueda = None
if 'puntos_vak' not in st.session_state:
    st.session_state.puntos_vak = None
if 'nombre_cliente' not in st.session_state:
    st.session_state.nombre_cliente = ""

# 2. BARRA LATERAL
with st.sidebar:
    st.title("🛠️ Suite GROW+")
    opcion = st.radio("Herramienta:", ["🎡 Rueda de la Vida", "🧠 Test VAK (Oficial)", "🤖 Consultoría IA"])
    
    st.divider()
    if st.button("🗑️ Nuevo Cliente / Limpiar Datos"):
        for key in ['datos_rueda', 'puntos_vak', 'nombre_cliente']:
            st.session_state[key] = None if key != 'nombre_cliente' else ""
        st.rerun()
    
    st.info("Especialidad: Coaching Estratégico")

# 3. DATOS DE LAS RUEDAS (64 Vectores)
ruedas_data = {
    "0. MAPA GENERAL (Macro)": ["Salud", "Economía", "Trabajo", "Des. Personal", "Familia", "Amor", "Amistad", "Diversión"],
    "2.1 SALUD": ["Sueño", "Nutrición", "Energía", "Movimiento", "Estrés", "Prevención", "Escucha Corporal", "Rutinas"],
    "2.2 ECONOMÍA": ["Ingresos", "Ahorro", "Deudas", "Control Gasto", "Relación Dinero", "Edu. Finan.", "Extras", "Seguridad"],
    "2.3 TRABAJO": ["Claridad", "Productividad", "Satisfacción", "Progresión", "Clima", "Autonomía", "Propósito", "Reconocimiento"],
    "2.4 DESARROLLO PERSONAL": ["Autoconocimiento", "Emociones", "Disciplina", "Narrativa", "Aprendizaje", "Valores", "Adaptación", "Evolución"],
    "2.5 FAMILIA": ["Comunicación", "Tiempo", "Apoyo", "Conflictos", "Límites", "Responsabilidad", "Presencia", "Unión"],
    "2.6 AMOR": ["Comunicación", "Intimidad", "Confianza", "Proyecto", "Conflictos", "Espacio", "Afecto", "Satisfacción"],
    "2.7 AMISTAD": ["Cantidad", "Profundidad", "Confianza", "Apoyo", "Diversidad", "Influencia", "Frecuencia", "Pertenencia"],
    "2.8 DIVERSIÓN": ["Tiempo", "Desconexión", "Placer", "Creatividad", "Juego", "Variedad", "Entorno", "Culpa"]
}

# --- SECCIÓN: RUEDA DE LA VIDA ---
if opcion == "🎡 Rueda de la Vida":
    st.write("# 📊 Diagnóstico Estratégico")
    
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.nombre_cliente = st.text_input("Nombre del Cliente:", value=st.session_state.nombre_cliente)
    with col2:
        area_sel = st.selectbox("Área a evaluar:", list(ruedas_data.keys()))

    vectores = ruedas_data[area_sel]
    valores = [st.slider(v, 1, 10, 5, key=f"s_{v}") for v in vectores]

    if st.button("🚀 GUARDAR Y VISUALIZAR", type="primary", use_container_width=True):
        st.session_state.datos_rueda = {"area": area_sel, "vectores": vectores, "valores": valores}
        
        N = len(vectores)
        angulos = [n / float(N) * 2 * np.pi for n in range(N)]
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        plt.xticks(angulos, vectores, size=10, weight='bold')
        ax.plot(angulos + [angulos[0]], valores + [valores[0]], color='#1A5276', linewidth=2)
        ax.fill(angulos + [angulos[0]], valores + [valores[0]], color='#5DADE2', alpha=0.4)
        st.pyplot(fig)

# --- SECCIÓN: TEST VAK ---
elif opcion == "🧠 Test VAK (Oficial)":
    st.write("# 🧠 Perfil Sensorial VAK")
    preguntas = ["1. Aprender juego", "2. Buscar hotel", "3. Software", "4. Ortografía", "5. Conferencia", "6. Montaje", "7. Jardinería", "8. Memoria", "9. Presentación", "10. Aficiones", "11. Nueva habilidad", "12. Enseñar"]
    
    totales = {"A": 0, "V": 0, "C": 0}
    for i, p in enumerate(preguntas):
        with st.expander(f"Situación: {p}"):
            c1, c2, c3 = st.columns(3)
            with c1: a = st.select_slider("A", options=range(1,8), value=4, key=f"a{i}")
            with c2: v = st.select_slider("V", options=range(1,8), value=4, key=f"v{i}")
            with c3: c = st.select_slider("C", options=range(1,8), value=4, key=f"c{i}")
            totales["A"] += a; totales["V"] += v; totales["C"] += c

    if st.button("📊 GUARDAR PERFIL VAK", type="primary", use_container_width=True):
        st.session_state.puntos_vak = totales
        st.success("Perfil guardado.")
        st.bar_chart(pd.DataFrame(totales.items(), columns=['Canal', 'Puntos']).set_index('Canal'))

# --- SECCIÓN: IA (GROW+ PROFESIONAL) ---
elif opcion == "🤖 Consultoría IA":
    st.write("# 🤖 Consultoría Estratégica GROW+")
    
    if "GEMINI_API_KEY" not in st.secrets:
        st.error("Falta la API Key en los Secrets de Streamlit.")
        st.stop()

    if not st.session_state.datos_rueda and not st.session_state.puntos_vak:
        st.warning("Sin datos previos para analizar.")
    else:
        pregunta = st.text_area("¿Cuál es el desafío estratégico hoy?", placeholder="Ej: No logra delegar en el trabajo...")
        
        if st.button("🧠 GENERAR ANÁLISIS GROW+", type="primary", use_container_width=True):
            with st.spinner("Analizando con Gemini 1.5 Flash..."):
                try:
                    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                    # Usamos una llamada más genérica al modelo para evitar el error 404
                    model = genai.GenerativeModel('models/gemini-1.5-flash')
                    
                    # Recopilar contexto
                    info = f"Cliente: {st.session_state.nombre_cliente}\n"
                    if st.session_state.datos_rueda:
                        info += f"Rueda {st.session_state.datos_rueda['area']}: {list(zip(st.session_state.datos_rueda['vectores'], st.session_state.datos_rueda['valores']))}\n"
                    if st.session_state.puntos_vak:
                        v = st.session_state.puntos_vak
                        pred = max(v, key=v.get)
                        info += f"VAK (Predominante {pred}): {v}\n"

                    # EL PROMPT ESTRATÉGICO GROW+
                    prompt = f"""
                    {info}
                    DESAFÍO: {pregunta}

                    Actúa como un Master Coach Estratégico. Genera:
                    1. REALIDAD (R): Identifica el 'Vector Palanca' y cómo el perfil sensorial del cliente afecta su bloqueo.
                    2. LENGUAJE SENSORIAL: Traduce la solución a predicados del canal {pred if st.session_state.puntos_vak else 'del cliente'}.
                    3. PREGUNTAS CLAVE: 5 preguntas GROW de alto impacto.
                    4. VOLUNTAD (W): Una tarea táctica específica.
                    """

                    response = model.generate_content(prompt)
                    st.divider()
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Error de conexión: {str(e)}")
