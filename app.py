import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import io
import pandas as pd

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Hathora - Suite de Coaching", layout="centered")

# Mantener el estado de la aplicación para evitar problemas en iPhone
if 'dibujar_rueda' not in st.session_state:
    st.session_state.dibujar_rueda = False

# 2. MENÚ DE NAVEGACIÓN LATERAL
with st.sidebar:
    st.title("🛠️ Suite para Coaches")
    opcion = st.radio("Selecciona herramienta:", ["🎡 Rueda de la Vida", "🧠 Test VAK (Oficial)", "🤖 Consultoría IA"])
    st.divider()
    st.info("Desarrollado para Claridad Estratégica")

# 3. DATOS DE LAS RUEDAS (Tu configuración original)
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

# --- SECCIÓN: RUEDA DE LA VIDA ---
if opcion == "🎡 Rueda de la Vida":
    st.write("# 📊 Sistema de Diagnóstico de 64 Vectores")
    
    with st.expander("📝 Datos del Informe", expanded=True):
        col1, col2 = st.columns(2)
        with col1: nombre = st.text_input("Nombre del Cliente:", key="n_rueda")
        with col2: area_seleccionada = st.selectbox("Área a evaluar:", list(ruedas_data.keys()))

    vectores = ruedas_data[area_seleccionada]
    valores = []
    st.write(f"### Puntuación: {area_seleccionada}")
    
    c1, c2 = st.columns(2)
    for i, v in enumerate(vectores):
        with (c1 if i % 2 == 0 else c2):
            val = st.slider(v, 1, 10, 5, key=f"s_{v}")
            valores.append(val)

    if st.button("🚀 GENERAR REPORTE", type="primary", use_container_width=True):
        st.session_state.dibujar_rueda = True

    if st.session_state.dibujar_rueda:
        N = len(vectores)
        angulos = [n / float(N) * 2 * np.pi for n in range(N)]
        valores_plot = valores + [valores[0]]
        angulos_plot = angulos + [angulos[0]]
        
        fig, ax = plt.subplots(figsize=(10, 12), subplot_kw=dict(polar=True))
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        plt.xticks(angulos, vectores, color='black', size=10, weight='bold')
        ax.plot(angulos_plot, valores_plot, color='#1A5276', linewidth=3)
        ax.fill(angulos_plot, valores_plot, color='#5DADE2', alpha=0.4)
        plt.title(f"DIAGNÓSTICO: {area_seleccionada}\nCliente: {nombre}", size=16, pad=30)
        
        st.pyplot(fig)
        
        img = io.BytesIO()
        fig.savefig(img, format='png', bbox_inches='tight', dpi=300)
        st.download_button("📥 DESCARGAR IMAGEN", img.getvalue(), f"Rueda_{nombre}.png", "image/png", use_container_width=True)
        
        if st.button("🔄 NUEVA EVALUACIÓN"):
            st.session_state.dibujar_rueda = False
            st.rerun()

# --- SECCIÓN: TEST VAK ---
elif opcion == "🧠 Test VAK (Oficial)":
    st.write("# 🧠 Test de Preferencias VAK")
    st.write("Escala del 1 (No lo utilizo apenas) al 7 (Refleja mi comportamiento a la perfección)")

    preguntas_vak = [
        "1. Aprender un juego nuevo de sobremesa",
        "2. Dificultad para encontrar un hotel",
        "3. Aprender un nuevo programa informático",
        "4. Al dudar cómo se escribe una palabra",
        "5. Al asistir a una clase o conferencia",
        "6. Al montar un artículo tú mismo",
        "7. Cuidar la casa o jardín de un amigo",
        "8. Recordar de memoria un número",
        "9. Realizar una presentación ante un grupo",
        "10. Disfrute de aficiones (Música, Dibujo, Paseo)",
        "11. Desarrollar una nueva habilidad",
        "12. Enseñar algo a alguien"
    ]

    totales = {"A": 0, "V": 0, "C": 0}

    for i, p in enumerate(preguntas_vak):
        with st.expander(f"Situación {p}", expanded=(i==0)):
            c1, c2, c3 = st.columns(3)
            with c1: a = st.select_slider("A (Auditivo)", options=range(1,8), value=4, key=f"vak_a_{i}")
            with c2: v = st.select_slider("V (Visual)", options=range(1,8), value=4, key=f"vak_v_{i}")
            with c3: c = st.select_slider("C (Cinestésico)", options=range(1,8), value=4, key=f"vak_c_{i}")
            totales["A"] += a
            totales["V"] += v
            totales["C"] += c

    if st.button("📊 ANALIZAR PERFIL VAK", type="primary", use_container_width=True):
        st.divider()
        st.write(f"### Resultados Finales")
        
        df_res = pd.DataFrame({
            "Canal": ["Auditivo", "Visual", "Cinestésico"],
            "Puntaje": [totales["A"], totales["V"], totales["C"]]
        })
        
        st.bar_chart(df_res.set_index("Canal"))
        
        def nivel(p):
            if p <= 41: return "BAJA (12-41)"
            if p <= 63: return "MEDIA (42-63)"
            return "ALTA (64-84)"

        col_a, col_v, col_c = st.columns(3)
        col_a.metric("Auditivo", totales["A"], nivel(totales["A"]))
        col_v.metric("Visual", totales["V"], nivel(totales["V"]))
        col_c.metric("Cinestésico", totales["C"], nivel(totales["C"]))

# --- SECCIÓN: IA ---
elif opcion == "🤖 Consultoría IA":
    st.write("# 🤖 Asistente Estratégico para el Coach")
    st.info("Conecta Gemini para analizar los resultados de las herramientas anteriores.")
    st.text_input("Introduce tu API Key de Google (Gemini):", type="password")
