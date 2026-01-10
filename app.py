import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import io
import pandas as pd
import google.generativeai as genai

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Hathora - Suite de Coaching Estratégico", layout="centered")

# --- INICIALIZACIÓN DE ESTADOS (Session State) ---
if 'datos_rueda' not in st.session_state:
    st.session_state.datos_rueda = None
if 'puntos_vak' not in st.session_state:
    st.session_state.puntos_vak = None
if 'nombre_cliente' not in st.session_state:
    st.session_state.nombre_cliente = ""

# 2. BARRA LATERAL (NAVEGACIÓN)
with st.sidebar:
    st.title("🛠️ Suite GROW+")
    opcion = st.radio("Herramienta:", ["🎡 Rueda de la Vida", "🧠 Test VAK (Oficial)", "🤖 Consultoría IA"])
    
    st.divider()
    if st.button("🗑️ Nuevo Cliente / Limpiar Datos"):
        st.session_state.datos_rueda = None
        st.session_state.puntos_vak = None
        st.session_state.nombre_cliente = ""
        st.rerun()
    
    st.info("Especialidad: Coaching Estratégico & GROW+")

# 3. BASE DE DATOS DE RUEDAS (64 VECTORES)
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

# --- SECCIÓN: RUEDA DE LA VIDA (CON ANÁLISIS AUTOMÁTICO) ---
if opcion == "🎡 Rueda de la Vida":
    st.write("# 📊 Diagnóstico Estratégico")
    
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.nombre_cliente = st.text_input("Nombre del Cliente:", value=st.session_state.nombre_cliente)
    with col2:
        area_sel = st.selectbox("Área a evaluar:", list(ruedas_data.keys()))

    vectores = ruedas_data[area_sel]
    valores = [st.slider(v, 1, 10, 5, key=f"s_{v}") for v in vectores]

    if st.button("🚀 GENERAR RUEDA Y ANÁLISIS IA", type="primary", use_container_width=True):
        st.session_state.datos_rueda = {"area": area_sel, "vectores": vectores, "valores": valores}
        
        # --- 1. GENERAR GRÁFICO ---
        N = len(vectores)
        angulos = [n / float(N) * 2 * np.pi for n in range(N)]
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        plt.xticks(angulos, vectores, size=10, weight='bold')
        ax.plot(angulos + [angulos[0]], valores + [valores[0]], color='#1A5276', linewidth=2)
        ax.fill(angulos + [angulos[0]], valores + [valores[0]], color='#5DADE2', alpha=0.4)
        st.pyplot(fig)

        # --- 2. ANÁLISIS AUTOMÁTICO CON IA ---
        st.divider()
        st.write("### 🤖 Diagnóstico Estratégico Instantáneo")
        
        if "GEMINI_API_KEY" in st.secrets:
            with st.spinner("Gemini analizando vectores..."):
                try:
                    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    
                    puntuaciones = list(zip(vectores, valores))
                    
                    # Prompt Estratégico Automático
                    prompt_auto = f"""
                    Eres un Master Coach Estratégico. Analiza esta Rueda de la Vida de {st.session_state.nombre_cliente}:
                    ÁREA: {area_sel}
                    PUNTUACIONES: {puntuaciones}

                    PROPORCIONA:
                    1. 🎯 VECTOR PALANCA: Identifica qué punto tiene más potencial de mejora para mover el resto del sistema.
                    2. 🔍 INSIGHT: Un breve análisis de la estructura actual.
                    3. ❓ PREGUNTA PODEROSA: Una pregunta de Coaching Estratégico basada en estos datos.
                    """
                    
                    response = model.generate_content(prompt_auto)
                    st.info(response.text)
                except Exception as e:
                    st.error(f"Error en análisis IA: {e}")
        else:
            st.warning("Configura GEMINI_API_KEY en Secrets para el análisis automático.")

# --- SECCIÓN: TEST VAK ---
elif opcion == "🧠 Test VAK (Oficial)":
    st.write("# 🧠 Perfil Sensorial VAK")
    preguntas = ["1. Juego nuevo", "2. Buscar hotel", "3. Software", "4. Ortografía", "5. Conferencia", "6. Montaje", "7. Jardinería", "8. Memoria", "9. Presentación", "10. Aficiones", "11. Nueva habilidad", "12. Enseñar"]
    
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
        st.success("Perfil sensorial guardado con éxito.")
        st.bar_chart(pd.DataFrame(totales.items(), columns=['Canal', 'Puntos']).set_index('Canal'))

# --- SECCIÓN: CONSULTORÍA IA (ANÁLISIS PROFUNDO GROW+) ---
elif opcion == "🤖 Consultoría IA":
    st.write("# 🤖 Consultoría Estratégica GROW+")
    
    if not st.session_state.datos_rueda:
        st.warning("⚠️ Debes generar una Rueda de la Vida primero para tener contexto.")
    else:
        st.success(f"Analizando contexto de: {st.session_state.nombre_cliente}")
        pregunta_coach = st.text_area("¿Cuál es el desafío o consulta específica?", placeholder="Ej: No logra establecer rutinas de sueño...")
        
        if st.button("🚀 GENERAR HOJA DE RUTA GROW+", type="primary", use_container_width=True):
            if "GEMINI_API_KEY" in st.secrets:
                with st.spinner("Gemini aplicando metodología GROW+..."):
                    try:
                        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        
                        # Recopilar todo el contexto disponible
                        rueda = st.session_state.datos_rueda
                        puntuaciones = list(zip(rueda['vectores'], rueda['valores']))
                        
                        vak_info = "No disponible"
                        predominancia = "el canal del cliente"
                        if st.session_state.puntos_vak:
                            v = st.session_state.puntos_vak
                            pred_code = max(v, key=v.get)
                            mapa = {"V": "Visual", "A": "Auditivo", "C": "Cinestésico"}
                            predominancia = mapa.get(pred_code, pred_code)
                            vak_info = f"{v} (Predominante: {predominancia})"

                        prompt_grow = f"""
                        Actúa como un Master Coach Estratégico experto en metodología GROW+.
                        CONTEXTO:
                        - Cliente: {st.session_state.nombre_cliente}
                        - Rueda {rueda['area']}: {puntuaciones}
                        - Perfil VAK: {vak_info}
                        - Desafío: {pregunta_coach}

                        ESTRUCTURA DE RESPUESTA:
                        1. 🔍 REALIDAD (R): Analiza el vector palanca bajo la óptica sensorial {predominancia}.
                        2. 💡 ESTRATEGIA: Propón un enfoque basado en Coaching Estratégico.
                        3. ❓ PREGUNTAS CLAVE: 5 preguntas potentes usando predicados {predominancia}.
                        4. 🎯 VOLUNTAD (W): Una tarea SMART específica.
                        """
                        
                        response = model.generate_content(prompt_grow)
                        st.divider()
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.error("API Key no configurada.")
