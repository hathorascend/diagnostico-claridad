import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from google import genai

# -------------------------------------------------
# CONFIGURACIÓN GENERAL
# -------------------------------------------------
st.set_page_config(
    page_title="Hathora | Coaching Estratégico",
    layout="centered"
)

# -------------------------------------------------
# SESSION STATE
# -------------------------------------------------
if "nombre_cliente" not in st.session_state:
    st.session_state.nombre_cliente = ""
if "datos_rueda" not in st.session_state:
    st.session_state.datos_rueda = None
if "diagnostico" not in st.session_state:
    st.session_state.diagnostico = None
if "puntos_vak" not in st.session_state:
    st.session_state.puntos_vak = None

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
with st.sidebar:
    st.title("🛠️ Hathora GROW+")
    opcion = st.radio(
        "Herramienta",
        ["🎡 Rueda de la Vida", "🧠 Test VAK", "🤖 Consultoría Estratégica"]
    )

    st.divider()
    if st.button("🗑️ Nuevo Cliente / Limpiar"):
        keys = list(st.session_state.keys())
        for k in keys:
            del st.session_state[k]
        st.rerun()

# -------------------------------------------------
# BASE DE DATOS RUEDAS
# -------------------------------------------------
ruedas_data = {
    "MAPA GENERAL": ["Salud", "Economía", "Trabajo", "Desarrollo", "Familia", "Amor", "Amistad", "Diversión"],
    "SALUD": ["Sueño", "Nutrición", "Energía", "Movimiento", "Estrés", "Prevención", "Rutinas", "Escucha corporal"],
    "ECONOMÍA": ["Ingresos", "Ahorro", "Deudas", "Control gasto", "Relación dinero", "Educación financiera", "Extras", "Seguridad"],
    "TRABAJO": ["Claridad", "Productividad", "Satisfacción", "Progresión", "Clima", "Autonomía", "Propósito", "Reconocimiento"]
}

# -------------------------------------------------
# CLIENT GEMINI
# -------------------------------------------------
def gemini_response(prompt):
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text

# -------------------------------------------------
# SECCIÓN 1 — RUEDA DE LA VIDA (DIAGNÓSTICO)
# -------------------------------------------------
if opcion == "🎡 Rueda de la Vida":
    st.title("📊 Diagnóstico Sistémico")

    st.session_state.nombre_cliente = st.text_input(
        "Nombre del cliente",
        value=st.session_state.nombre_cliente
    )

    area = st.selectbox("Área a evaluar", list(ruedas_data.keys()))
    vectores = ruedas_data[area]
    valores = [st.slider(v, 1, 10, 5, key=f"s_{v}") for v in vectores]

    if st.button("🚀 Generar Diagnóstico", use_container_width=True):
        st.session_state.datos_rueda = {
            "area": area,
            "vectores": vectores,
            "valores": valores
        }

        # --- GRÁFICO ---
        N = len(vectores)
        angles = np.linspace(0, 2 * np.pi, N, endpoint=False)
        valores_plot = valores + [valores[0]]
        angles_plot = list(angles) + [angles[0]]

        fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        ax.plot(angles_plot, valores_plot)
        ax.fill(angles_plot, valores_plot, alpha=0.3)
        ax.set_thetagrids(angles * 180 / np.pi, vectores)
        st.pyplot(fig)
        plt.close(fig)

        # --- PROMPT MAESTRO (CAPA 1) ---
        puntuaciones = list(zip(vectores, valores))

        prompt_diagnostico = f"""
Actúa como un Master Coach Estratégico con enfoque sistémico.

Cliente: {st.session_state.nombre_cliente}
Área evaluada: {area}
Vectores y puntuaciones: {puntuaciones}

REGLAS:
- No describas los datos.
- No repitas puntuaciones.
- No lenguaje motivacional genérico.
- Máx 150 palabras.
- Responde en bullets.

ANÁLISIS:
1. Tensión central del sistema.
2. Vector bloqueador real.
3. Hipótesis conductual observable.
4. Palanca de alto impacto (1 acción).
5. Coste oculto de mantener este estado.
6. Pregunta maestra de confrontación.
"""

        st.session_state.diagnostico = gemini_response(prompt_diagnostico)

        st.divider()
        st.subheader("🔍 Diagnóstico Estratégico")
        st.info(st.session_state.diagnostico)

# -------------------------------------------------
# SECCIÓN 2 — TEST VAK
# -------------------------------------------------
elif opcion == "🧠 Test VAK":
    st.title("🧠 Perfil Sensorial VAK")

    preguntas = range(1, 13)
    totales = {"V": 0, "A": 0, "C": 0}

    for i in preguntas:
        with st.expander(f"Situación {i}"):
            v = st.slider("Visual", 1, 7, 4, key=f"v{i}")
            a = st.slider("Auditivo", 1, 7, 4, key=f"a{i}")
            c = st.slider("Cinestésico", 1, 7, 4, key=f"c{i}")
            totales["V"] += v
            totales["A"] += a
            totales["C"] += c

    if st.button("Guardar Perfil", use_container_width=True):
        st.session_state.puntos_vak = totales
        st.success("Perfil VAK guardado")
        st.bar_chart(pd.DataFrame(totales.values(), index=totales.keys()))

# -------------------------------------------------
# SECCIÓN 3 — CONSULTORÍA ESTRATÉGICA (CAPA 2 + 3)
# -------------------------------------------------
elif opcion == "🤖 Consultoría Estratégica":
    st.title("🤖 Consultoría GROW+")

    if not st.session_state.diagnostico:
        st.warning("Primero genera una Rueda de la Vida.")
    else:
        consulta = st.text_area("Desafío específico del cliente")

        pred = "Visual"
        if st.session_state.puntos_vak:
            pred = max(st.session_state.puntos_vak, key=st.session_state.puntos_vak.get)
            pred = {"V": "Visual", "A": "Auditivo", "C": "Cinestésico"}[pred]

        if st.button("🚀 Generar Hoja de Ruta", use_container_width=True):
            prompt_grow = f"""
Actúa como un Coach Estratégico experto en metodología GROW+.

DIAGNÓSTICO BASE:
{st.session_state.diagnostico}

Desafío declarado:
{consulta}

Perfil sensorial predominante: {pred}

REGLAS:
- No repitas el diagnóstico.
- Lenguaje claro y accionable.
- Usa predicados {pred}.
- Máx 200 palabras.

RESPONDE:
1. REALIDAD (R): cómo se manifiesta esta tensión hoy.
2. OPCIONES (O): 3 caminos viables.
3. VOLUNTAD (W): 1 acción SMART concreta para 7 días.
"""

            respuesta = gemini_response(prompt_grow)
            st.divider()
            st.subheader("🎯 Hoja de Ruta Estratégica")
            st.markdown(respuesta)
