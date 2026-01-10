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

# 2. NAVEGACIÓN Y CONTROL LATERAL
with st.sidebar:
    st.title("🛠️ Suite GROW+")
    opcion = st.radio("Herramienta:", ["🎡 Rueda de la Vida", "🧠 Test VAK (Oficial)", "🤖 Consultoría IA"])
    
    st.divider()
    if st.button("🗑️ Limpiar / Nuevo Cliente"):
        st.session_state.datos_rueda = None
        st.session_state.puntos_vak = None
        st.session_state.nombre_cliente = ""
        st.rerun()
    
    st.info("Configurado para Coaching Estratégico")

# 3. DATOS DE LAS RUEDAS
ruedas_data = {
    "0. MAPA GENERAL (Macro)": ["Salud", "Economía", "Trabajo", "Des. Personal", "Familia", "Amor", "Amistad", "Diversión"],
    "2.1 SALUD (Cuerpo y Energía)": ["Sueño/Descanso", "Nutrición", "Energía Diaria", "Movimiento", "Gestión Estrés", "Salud Preventiva", "Escucha Corporal", "Rutinas Sólidas"],
    "2.2 ECONOMÍA (Finanzas)": ["Nivel Ingresos", "Capacidad Ahorro", "Gestión Deudas", "Control Gasto", "Relación Dinero", "Edu. Finan.", "Ingresos Extra", "Seguridad Finan."],
    "2.3 TRABAJO (Carrera)": ["Claridad Rol", "Productividad", "Satisfacción", "Progresión", "Clima Laboral", "Autonomía", "Propósito", "Reconocimiento"],
    "2.4 DESARROLLO PERSONAL": ["Autoconocimiento", "Gestión Emocional", "Disciplina", "Narrativa Interna", "Aprendizaje", "Valores Claros", "Adaptación", "Sentido Evolución"],
    "2.5 FAMILIA": ["Comunicación", "Tiempo Calidad", "Apoyo Emocional", "Res. Conflictos", "Límites Sanos", "Resp. Compartida", "Presencia Real", "Unión"],
    "2.6 AMOR (Pareja)": ["Com. Emocional", "Intimidad", "Confianza", "Proyecto Común", "Gestión Conflictos", "Espacio Indiv.", "Afecto", "Satisfacción"],
    "2.7 AMISTAD (Social)": ["Cantidad Activa", "Profundidad", "Confianza", "Apoyo", "Diversidad", "Influencia (+)", "Frecuencia", "Pertenencia"],
    "2.8 DIVERSIÓN (Ocio)": ["Tiempo Disfrute", "Desconexión", "Placer Real", "Creatividad", "Risa/Juego", "Variedad", "Cambio Entorno", "Permiso/Culpa"]
}

# --- LÓGICA DE IA (Función Reutilizable) ---
def consultar_gemini(prompt_personalizado):
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Construcción del contexto dinámico
        contexto_datos = f"Cliente: {st.session_state.nombre_cliente}\n"
        if st.session_state.datos_rueda:
            d = st.session_state.datos_rueda
            contexto_datos += f"RUEDA {d['area']}: {list(zip(d['vectores'], d['valores']))}\n"
        if st.session_state.puntos_vak:
            v = st.session_state.puntos_vak
            pred = max(v, key=v.get)
            contexto_datos += f"VAK: A:{v['A']}, V:{v['V']}, C:{v['C']} (Predominante: {pred})\n"
        
        prompt_final = f"""
        Eres un Master Coach Estratégico experto en metodología GROW+.
        CONTEXTO ACTUAL:
        {contexto_datos}
        
        OBJETIVO:
        {prompt_personalizado}
        
        RESPUESTA: Estructurada, profesional y lista para la sesión.
        """
        
        response = model.generate_content(prompt_final)
        return response.text
    except Exception as e:
        return f"Error: Configura la API Key en los Secrets de Streamlit. ({str(e)})"

# --- SECCIÓN: RUEDA DE LA VIDA ---
if opcion == "🎡 Rueda de la Vida":
    st.write("# 📊 Diagnóstico Estratégico")
    
    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("Nombre del Cliente:", value=st.session_state.nombre_cliente)
        st.session_state.nombre_cliente = nombre
    with col2:
        area_sel = st.selectbox("Área a evaluar:", list(ruedas_data.keys()))

    vectores = ruedas_data[area_sel]
    valores = []
    
    st.write(f"### Puntuación: {area_sel}")
    c1, c2 = st.columns(2)
    for i, v in enumerate(vectores):
        with (c1 if i % 2 == 0 else c2):
            val = st.slider(v, 1, 10, 5, key=f"s_{v}")
            valores.append(val)

    if st.button("🚀 GENERAR REPORTE", type="primary", use_container_width=True):
        st.session_state.datos_rueda = {"area": area_sel, "vectores": vectores, "valores": valores}
        
        N = len(vectores)
        angulos = [n / float(N) * 2 * np.pi for n in range(N)]
        v_plot = valores + [valores[0]]
        a_plot = angulos + [angulos[0]]
        
        fig, ax = plt.subplots(figsize=(8, 10), subplot_kw=dict(polar=True))
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        plt.xticks(angulos, vectores, size=9, weight='bold')
        ax.plot(a_plot, v_plot, color='#1A5276', linewidth=2)
        ax.fill(a_plot, v_plot, color='#5DADE2', alpha=0.4)
        plt.title(f"{area_sel}\nCliente: {nombre}", size=14, pad=20)
        st.pyplot(fig)
        
        img = io.BytesIO()
        fig.savefig(img, format='png', bbox_inches='tight')
        st.download_button("📥 DESCARGAR IMAGEN", img.getvalue(), f"Rueda_{area_sel}.png", "image/png")

# --- SECCIÓN: TEST VAK ---
elif opcion == "🧠 Test VAK (Oficial)":
    st.write("# 🧠 Perfil de Comunicación Sensorial")
    st.caption("Basado en el Test del Instituto Canario de Coaching")

    preguntas = ["1. Juego nuevo", "2. Buscar hotel", "3. Nuevo software", "4. Ortografía", 
                 "5. Conferencia", "6. Montaje", "7. Jardinería", "8. Memoria", 
                 "9. Presentación", "10. Aficiones", "11. Nueva habilidad", "12. Enseñar"]

    totales = {"A": 0, "V": 0, "C": 0}
    for i, p in enumerate(preguntas):
        with st.expander(f"Situación: {p}"):
            ca, cv, cc = st.columns(3)
            with ca: a = st.select_slider("A", options=range(1,8), value=4, key=f"va{i}")
            with cv: v = st.select_slider("V", options=range(1,8), value=4, key=f"vv{i}")
            with cc: c = st.select_slider("C", options=range(1,8), value=4, key=f"vc{i}")
            totales["A"] += a; totales["V"] += v; totales["C"] += c

    if st.button("📊 GUARDAR RESULTADOS VAK", type="primary", use_container_width=True):
        st.session_state.puntos_vak = totales
        st.success("Perfil guardado con éxito.")
        
        df_vak = pd.DataFrame({"Canal": ["Auditivo", "Visual", "Cinestésico"], "Puntos": [totales["A"], totales["V"], totales["C"]]})
        st.bar_chart(df_vak.set_index("Canal"))

# --- SECCIÓN: CONSULTORÍA IA (GROW+) ---
elif opcion == "🤖 Consultoría IA":
    st.write("# 🤖 Analizador Estratégico GROW+")
    
    if not st.session_state.datos_rueda and not st.session_state.puntos_vak:
        st.warning("⚠️ Sin datos. Por favor, completa la Rueda o el VAK primero.")
    else:
        st.success(f"Analizando a: {st.session_state.nombre_cliente}")
        
        pregunta_coach = st.text_area("Enfoque de la consulta:", placeholder="Ej: ¿Cómo abordar la falta de disciplina en este cliente?")
        
        if st.button("🚀 GENERAR ANÁLISIS ESTRATÉGICO", type="primary"):
            with st.spinner("Gemini procesando diagnóstico..."):
                predominancia = "el canal predominante"
                if st.session_state.puntos_vak:
                    v = st.session_state.puntos_vak
                    predominancia = max(v, key=v.get)
                
                # EL PROMPT ESTRATÉGICO
                p_maestro = f"""
                Analiza al cliente usando GROW+.
                1. REALIDAD (R): Basado en la rueda, identifica el 'vector palanca' (el que más impacto tiene).
                2. LENGUAJE: El cliente es {predominancia}. Traduce los insights a predicados sensoriales de este canal.
                3. PREGUNTAS CLAVE: Genera 5 preguntas poderosas GROW para que el cliente pase a la acción.
                4. TAREA SUGERIDA: Una acción SMART para esta semana.
                
                CONSULTA EXTRA DEL COACH: {pregunta_coach}
                """
                
                resultado = consultar_gemini(p_maestro)
                st.markdown("---")
                st.markdown(resultado)
