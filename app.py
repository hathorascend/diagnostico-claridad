import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import io

# Configuración de la página (Título en la pestaña del navegador)
st.set_page_config(page_title="Diagnóstico de Claridad", layout="centered")

# 1. DATOS DE LAS RUEDAS
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

# 2. INTERFAZ DE USUARIO (Sidebar)
st.title("🚀 Sistema de Claridad Fase 1")
st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    nombre = st.text_input("Nombre:", placeholder="Tu nombre aquí")
with col2:
    area_seleccionada = st.selectbox("Área a evaluar:", list(ruedas_data.keys()))

st.write(f"### Evalúa los vectores de: {area_seleccionada}")

# 3. GENERACIÓN DE SLIDERS DINÁMICOS
valores = []
vectores = ruedas_data[area_seleccionada]

# Creamos columnas para que los sliders no ocupen tanto espacio vertical
c1, c2 = st.columns(2)
for i, v in enumerate(vectores):
    with (c1 if i % 2 == 0 else c2):
        val = st.slider(v, 1, 10, 5, key=v)
        valores.append(val)

# 4. LÓGICA DEL GRÁFICO
if st.button("GENERAR DIAGNÓSTICO", type="primary"):
    N = len(vectores)
    angulos = [n / float(N) * 2 * np.pi for n in range(N)]
    valores_plot = valores + [valores[0]]
    angulos_plot = angulos + [angulos[0]]
    fecha = datetime.now().strftime("%d-%m-%Y")

    fig = plt.figure(figsize=(10, 15))
    ax = fig.add_subplot(111, polar=True)
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    
    plt.xticks(angulos, vectores, color='black', size=11, weight='bold')
    ax.set_rlabel_position(0)
    plt.yticks([2, 4, 6, 8, 10], ["2","4","6","8","10"], color="grey", size=8)
    plt.ylim(0, 10)
    
    ax.plot(angulos_plot, valores_plot, color='#1A5276', linewidth=2)
    ax.fill(angulos_plot, valores_plot, color='#5DADE2', alpha=0.5)
    
    plt.title(f"DIAGNÓSTICO: {area_seleccionada.upper()}", size=16, weight='bold', color='#1B4F72', pad=80)
    plt.suptitle(f"Nombre: {nombre if nombre else 'Anónimo'}  |  Fecha: {fecha}", fontsize=13, y=0.88, style='italic', color='#444444')

    # Mostrar en la web
    st.pyplot(fig)

    # Botón de descarga
    img = io.BytesIO()
    fig.savefig(img, format='png', bbox_inches='tight', dpi=300)
    st.download_button(
        label="📥 DESCARGAR RESULTADOS (PNG)",
        data=img.getvalue(),
        file_name=f"Diagnostico_{area_seleccionada}.png",
        mime="image/png"
    )
