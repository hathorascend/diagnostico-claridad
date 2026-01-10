# app.py
# BeCoach — Suite de Coaching Estratégico (UI Pro + VAK 24 + Copiloto + PDF)
# Requisitos: streamlit, matplotlib, numpy, pandas, google-generativeai, reportlab

import io
from datetime import datetime

import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import google.generativeai as genai

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# -------------------------
# CONFIG
# -------------------------
st.set_page_config(
    page_title="BeCoach - Suite de Coaching Estratégico",
    layout="wide",
    page_icon="BC",
)

# -------------------------
# CSS (Interfaz limpia)
# -------------------------
st.markdown(
    """
<style>
.block-container {padding-top: 1.1rem; padding-bottom: 2rem; max-width: 1200px;}
[data-testid="stSidebar"] {padding-top: 1rem;}
.h-card {
  border: 1px solid rgba(255,255,255,0.10);
  border-radius: 18px;
  padding: 14px 16px;
  background: rgba(255,255,255,0.03);
}
.h-kpi {font-size: 1.25rem; font-weight: 800;}
.h-small {opacity:0.86; font-size: 0.94rem; line-height: 1.3;}
.h-pill {
  display:inline-block; padding: 3px 10px; border-radius: 999px;
  background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.09);
  font-size: 0.85rem; margin-right: 6px;
}
hr {border: none; border-top: 1px solid rgba(255,255,255,0.10); margin: 12px 0;}
</style>
""",
    unsafe_allow_html=True,
)

# -------------------------
# SESSION STATE
# -------------------------
DEFAULTS = {
    "nombre_coach": "",
    "nombre_cliente": "",
    "objetivo_sesion": "",
    "nivel_cliente": "Nuevo",
    "datos_rueda": None,             # {"area": str, "vectores": [str], "valores":[int]}
    "puntos_vak": None,              # {"V": int, "A": int, "C": int}
    "diagnostico_generado": None,    # str
    "chat_hist": [],                 # [{"role":"user|assistant", "content": str}]
    "area_sel": "0. MAPA GENERAL (Macro)",
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


def reset_app():
    for k, v in DEFAULTS.items():
        st.session_state[k] = v
    st.toast("Sesión limpia ✅", icon="🧹")


def has_api_key() -> bool:
    return "GEMINI_API_KEY" in st.secrets and bool(st.secrets["GEMINI_API_KEY"])


def get_model():
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    return genai.GenerativeModel("gemini-2.5-flash")


# -------------------------
# DATA: RUEDAS
# -------------------------
ruedas_data = {
    "0. MAPA GENERAL (Macro)": ["Salud", "Economía", "Trabajo", "Des. Personal", "Familia", "Amor", "Amistad", "Diversión"],
    "2.1 SALUD": ["Sueño", "Nutrición", "Energía", "Movimiento", "Estrés", "Prevención", "Escucha Corporal", "Rutinas"],
    "2.2 ECONOMÍA": ["Ingresos", "Ahorro", "Deudas", "Control Gasto", "Relación Dinero", "Edu. Finan.", "Extras", "Seguridad"],
    "2.3 TRABAJO": ["Claridad", "Productividad", "Satisfacción", "Progresión", "Clima", "Autonomía", "Propósito", "Reconocimiento"],
    "2.4 DESARROLLO PERSONAL": ["Autoconocimiento", "Emociones", "Disciplina", "Narrativa", "Aprendizaje", "Valores", "Adaptación", "Evolución"],
    "2.5 FAMILIA": ["Comunicación", "Tiempo", "Apoyo", "Conflictos", "Límites", "Responsabilidad", "Presencia", "Unión"],
    "2.6 AMOR": ["Comunicación", "Intimidad", "Confianza", "Proyecto", "Conflictos", "Espacio", "Afecto", "Satisfacción"],
    "2.7 AMISTAD": ["Cantidad", "Profundidad", "Confianza", "Apoyo", "Diversidad", "Influencia", "Frecuencia", "Pertenencia"],
    "2.8 DIVERSIÓN": ["Tiempo", "Desconexión", "Placer", "Creatividad", "Juego", "Variedad", "Entorno", "Culpa"],
}

# -------------------------
# DATA: VAK 24 (escena + V/A/C)
# -------------------------
VAK_ITEMS = [
    {
        "titulo": "Instrucciones",
        "escena": "Debes ensamblar un objeto o aprender un proceso técnico nuevo (sin ayuda). ¿Qué te facilita más hacerlo bien?",
        "V": "Ver un diagrama/video paso a paso y una lista visual de piezas.",
        "A": "Escuchar una explicación clara o que alguien me lo explique en voz alta.",
        "C": "Probar con las manos, ajustar sobre la marcha y aprender haciendo.",
    },
    {
        "titulo": "Orientación",
        "escena": "Estás en una zona desconocida y necesitas llegar a una dirección sin perder tiempo.",
        "V": "Un mapa/referencias visuales (edificios, colores, formas) para ubicarme.",
        "A": "Indicaciones verbales (izquierda/derecha) o preguntar y repetir la ruta.",
        "C": "Caminar un tramo, sentir si voy bien y corregir por intuición de recorrido.",
    },
    {
        "titulo": "Distracción",
        "escena": "Estás trabajando concentrado y algo te interrumpe. ¿Qué te saca más de foco?",
        "V": "Movimiento, pantallas, notificaciones, desorden visual.",
        "A": "Ruidos, conversaciones cerca, sonidos repetitivos.",
        "C": "Incomodidad física, hambre, tensión corporal, ganas de moverme.",
    },
    {
        "titulo": "Memoria de Viajes",
        "escena": "Piensas en unas vacaciones pasadas. ¿Qué se te viene primero a la mente?",
        "V": "Imágenes del lugar, paisajes, fotos mentales de escenas.",
        "A": "Música/sonidos del sitio o conversaciones que recuerdo.",
        "C": "Sensaciones: clima, olor, energía del lugar, cómo me sentía.",
    },
    {
        "titulo": "Comunicación",
        "escena": "Necesitas contactar a alguien y recibir info importante. ¿Qué prefieres?",
        "V": "Mensaje escrito con puntos claros o un resumen visual.",
        "A": "Llamada/nota de voz para captar matices rápido.",
        "C": "Hablar en persona o una interacción que ‘se sienta’ directa.",
    },
    {
        "titulo": "Resolución de Problemas",
        "escena": "Un aparato no funciona. ¿Qué haces primero?",
        "V": "Busco manual/video/foros; reviso pasos y señales visibles.",
        "A": "Pregunto a alguien o escucho una explicación de qué revisar.",
        "C": "Toco, pruebo, reinicio, hago tests físicos y ajusto.",
    },
    {
        "titulo": "Conferencia / Clase",
        "escena": "Sales de una clase y mañana te evaluarán. ¿Cómo retienes mejor lo escuchado?",
        "V": "Recuerdo diapositivas, títulos, gráficos y estructura.",
        "A": "Recuerdo frases, ejemplos y el tono del docente.",
        "C": "Recuerdo lo que me hizo sentir y lo que ‘me quedó en el cuerpo’.",
    },
    {
        "titulo": "Nuevas Adquisiciones",
        "escena": "Vas a comprar un gadget (móvil, reloj, auriculares). ¿Qué te decide más?",
        "V": "Comparativas, specs, reviews con imágenes y tablas.",
        "A": "Recomendación de alguien o reseñas que expliquen bien el uso.",
        "C": "Probarlo en mano: peso, tacto, comodidad, sensación real.",
    },
    {
        "titulo": "Tiempo Libre",
        "escena": "Tienes una tarde libre. ¿Qué actividad te recarga más?",
        "V": "Ver algo (serie, fotos, museo) o crear algo visual.",
        "A": "Música, podcast, conversar, escuchar algo que me active.",
        "C": "Moverme: caminar, deporte, cocinar, actividades físicas.",
    },
    {
        "titulo": "Memoria de Personas",
        "escena": "Conoces a alguien nuevo. ¿Qué recuerdas primero de esa persona?",
        "V": "Cara, gestos, ropa, mirada, detalles visuales.",
        "A": "Nombre, voz, forma de hablar, frases que dijo.",
        "C": "Energía, vibra, apretón de manos, cómo me hizo sentir.",
    },
    {
        "titulo": "Predicados Verbales",
        "escena": "Sin pensarlo, ¿qué tipo de frases te salen más al hablar?",
        "V": "“Veo claro”, “me enfoca”, “se nota”, “imagina esto”.",
        "A": "“Suena bien”, “dime”, “escucha”, “eso no me cuadra”.",
        "C": "“Siento que”, “me pesa”, “me mueve”, “no me encaja”.",
    },
    {
        "titulo": "Concentración",
        "escena": "¿Qué ambiente te ayuda más a rendir intelectualmente?",
        "V": "Orden, buena luz, escritorio limpio, cero estímulos visuales.",
        "A": "Silencio o sonido controlado (música específica).",
        "C": "Comodidad física: postura, temperatura, pausas de movimiento.",
    },
    {
        "titulo": "Manejo de Estrés",
        "escena": "Surge una crisis/urgencia. ¿Qué te calma y te activa mejor?",
        "V": "Ver el plan por escrito y ordenar prioridades en una lista.",
        "A": "Hablarlo para aclarar y escuchar un plan directo.",
        "C": "Respirar, moverme y ejecutar una primera acción inmediata.",
    },
    {
        "titulo": "Aprendizaje de Software",
        "escena": "Abres una app nueva. ¿Cómo aprendes más rápido?",
        "V": "Exploro menús y miro tutoriales/guías visuales.",
        "A": "Sigo instrucciones narradas o alguien me explica.",
        "C": "Toco botones, ensayo-error y aprendo por uso.",
    },
    {
        "titulo": "Habilidades Sociales",
        "escena": "¿Qué genera confianza o ‘clic’ con un desconocido?",
        "V": "Su mirada/gestos coherentes y cómo se presenta visualmente.",
        "A": "Su tono, forma de hablar y claridad al comunicarse.",
        "C": "La energía que transmite y cómo me hace sentir en el momento.",
    },
    {
        "titulo": "Recepción de Feedback",
        "escena": "Te van a evaluar desempeño. ¿Cómo prefieres recibir feedback?",
        "V": "Documento con puntos, ejemplos y plan de mejora.",
        "A": "Conversación directa (llamada) con explicaciones claras.",
        "C": "Práctico: demo, acompañamiento, hacerlo juntos y corregir.",
    },
    {
        "titulo": "Descanso Mental",
        "escena": "Tras un día agotador, ¿qué te desconecta mejor?",
        "V": "Contenido visual ligero o algo creativo visual.",
        "A": "Música/podcast/charla que me relaje.",
        "C": "Ducha, caminata, estiramientos, descanso físico real.",
    },
    {
        "titulo": "Memoria de Corto Plazo",
        "escena": "Te dictan un número (teléfono/código) una vez. ¿Qué haces para retenerlo?",
        "V": "Lo visualizo escrito o lo ‘veo’ en mi mente.",
        "A": "Lo repito en voz baja varias veces.",
        "C": "Lo marco con dedos/ritmo o lo asocio a una acción/sensación.",
    },
    {
        "titulo": "Decisión de Compra (Ropa)",
        "escena": "Estás en el probador. ¿Qué define si compras la prenda?",
        "V": "Cómo se ve: corte, color, estilo, espejo.",
        "A": "Opinión de alguien o explicación de calidad/marca.",
        "C": "Cómo se siente: tela, comodidad, libertad de movimiento.",
    },
    {
        "titulo": "Proyectos en Grupo",
        "escena": "En un trabajo en equipo, ¿qué rol asumes naturalmente?",
        "V": "Organizo estructura, tableros, planificación visual.",
        "A": "Coordino comunicación, alineo conversaciones, sintetizo acuerdos.",
        "C": "Ejecuto tareas, destrabo acciones, pongo el cuerpo al trabajo.",
    },
    {
        "titulo": "Lectura de Placer",
        "escena": "Cuando lees por placer, ¿qué disfrutas más?",
        "V": "Descripciones, escenas, ideas que puedo visualizar.",
        "A": "El ritmo del texto, diálogos, ‘voz’ del autor.",
        "C": "La emoción/impacto que me deja, cómo me transforma.",
    },
    {
        "titulo": "Seguridad / Confort",
        "escena": "Llegas a un lugar nuevo. ¿Qué te da sensación de bienestar?",
        "V": "Ver la disposición del espacio, salidas, orden y claridad.",
        "A": "Escuchar el ambiente: volumen, tono, si hay ruido agradable.",
        "C": "Sentir el lugar: temperatura, comodidad, energía.",
    },
    {
        "titulo": "Transmisión de Conocimiento",
        "escena": "Tienes que explicar algo complejo a otra persona. ¿Cómo lo haces mejor?",
        "V": "Con un esquema/dibujo y pasos en pizarra/pantalla.",
        "A": "Hablándolo con ejemplos y repitiendo lo clave.",
        "C": "Haciéndolo juntos: práctica guiada paso a paso.",
    },
    {
        "titulo": "Búsqueda de Objetos",
        "escena": "Perdiste algo (llaves, móvil). ¿Qué haces primero?",
        "V": "Escaneo visual por zonas y recuerdo dónde lo vi por última vez.",
        "A": "Repaso en voz alta la secuencia: ‘llegué, dejé, volví…’.",
        "C": "Rehago movimientos: camino la ruta y ‘siento’ dónde estuvo.",
    },
]

# -------------------------
# PDF EXPORT
# -------------------------
def build_pdf_bytes() -> bytes:
    styles = getSampleStyleSheet()
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, title="Registro de Sesión BeCoach")
    story = []

    def P(text: str) -> Paragraph:
        return Paragraph(text, styles["BodyText"])

    # Portada simple
    story.append(Paragraph("BeCocach — Registro de Sesión", styles["Title"]))
    story.append(Spacer(1, 10))

    story.append(P(f"<b>Coach:</b> {st.session_state.nombre_coach or '—'}"))
    story.append(P(f"<b>Cliente:</b> {st.session_state.nombre_cliente or '—'}"))
    story.append(P(f"<b>Objetivo:</b> {st.session_state.objetivo_sesion or '—'}"))
    story.append(P(f"<b>Nivel:</b> {st.session_state.nivel_cliente or '—'}"))
    story.append(P(f"<b>Fecha:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}"))
    story.append(Spacer(1, 12))

    # Rueda
    story.append(Paragraph("Rueda", styles["Heading2"]))
    rueda = st.session_state.datos_rueda
    if rueda:
        story.append(P(f"<b>Área:</b> {rueda['area']}"))
        data = [["Vector", "Puntuación"]] + [[v, str(val)] for v, val in zip(rueda["vectores"], rueda["valores"])]
        t = Table(data, colWidths=[330, 130])
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("ALIGN", (1, 1), (1, -1), "CENTER"),
                ]
            )
        )
        story.append(t)
    else:
        story.append(P("No se generó rueda."))
    story.append(Spacer(1, 12))

    # Hipótesis IA
    story.append(Paragraph("Hipótesis conductual (IA)", styles["Heading2"]))
    hypo = st.session_state.diagnostico_generado or "No disponible."
    story.append(P(hypo.replace("\n", "<br/>")))
    story.append(Spacer(1, 12))

    # VAK
    story.append(Paragraph("Perfil VAK", styles["Heading2"]))
    vak = st.session_state.puntos_vak
    if vak:
        data = [["Canal", "Puntos"]] + [[k, str(vak.get(k, 0))] for k in ["V", "A", "C"]]
        t = Table(data, colWidths=[130, 130])
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("ALIGN", (1, 1), (1, -1), "CENTER"),
                ]
            )
        )
        story.append(t)
    else:
        story.append(P("No disponible."))
    story.append(Spacer(1, 12))

    # Chat Copiloto
    story.append(Paragraph("Copiloto — Registro de sesión", styles["Heading2"]))
    if st.session_state.chat_hist:
        for m in st.session_state.chat_hist:
            role = "COACH/CLIENTE" if m["role"] == "user" else "IA"
            story.append(P(f"<b>{role}:</b> {m['content'].replace('\n', '<br/>')}"))
            story.append(Spacer(1, 6))
    else:
        story.append(P("Sin conversación registrada."))

    doc.build(story)
    pdf = buf.getvalue()
    buf.close()
    return pdf


# -------------------------
# SIDEBAR
# -------------------------
with st.sidebar:
    st.title("🛠️ BeCoaCh GROW+")
    st.caption("Interfaz para sesión real + registro PDF.")

    st.divider()
    st.button("🧹 Nuevo cliente / Limpiar", use_container_width=True, on_click=reset_app)

    st.divider()
    st.markdown("**Estado**")
    st.write(f"- Rueda: {'✅' if st.session_state.datos_rueda else '—'}")
    st.write(f"- VAK: {'✅' if st.session_state.puntos_vak else '—'}")
    st.write(f"- Hipótesis IA: {'✅' if st.session_state.diagnostico_generado else '—'}")
    st.write(f"- Copiloto: {'✅' if st.session_state.chat_hist else '—'}")

    st.divider()
    if not has_api_key():
        st.warning("Falta `GEMINI_API_KEY` en Secrets (IA desactivada).")


# -------------------------
# HEADER
# -------------------------
now = datetime.now().strftime("%d/%m/%Y %H:%M")
chips = []
if st.session_state.datos_rueda:
    chips.append("Rueda ✅")
if st.session_state.puntos_vak:
    chips.append("VAK ✅")
if st.session_state.diagnostico_generado:
    chips.append("Hipótesis ✅")
if st.session_state.chat_hist:
    chips.append("Copiloto ✅")

chips_html = " ".join([f"<span class='h-pill'>{c}</span>" for c in chips]) or "<span class='h-pill'>Sin registros</span>"

st.markdown(
    f"""
<div class="h-card">
  <div class="h-kpi">🜂 BeCoach — Registro de Sesión</div>
  <div class="h-small">
    Coach: <b>{st.session_state.nombre_coach or "—"}</b> ·
    Cliente: <b>{st.session_state.nombre_cliente or "—"}</b> ·
    Objetivo: <b>{st.session_state.objetivo_sesion or "—"}</b> ·
    {now}
  </div>
  <div style="margin-top:8px;">{chips_html}</div>
</div>
""",
    unsafe_allow_html=True,
)

st.write("")

# -------------------------
# TABS (Flujo)
# -------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs(["1) Ficha", "2) Rueda", "3) Hipótesis IA", "4) VAK 24", "5) Copiloto + PDF"])

# -------------------------
# TAB 1: FICHA
# -------------------------
with tab1:
    st.subheader("1) Ficha de sesión")
    with st.form("ficha_form", clear_on_submit=False):
        c1, c2, c3, c4 = st.columns([1.3, 1.3, 1.4, 1])
        with c1:
            coach = st.text_input("Nombre del coach", value=st.session_state.nombre_coach, placeholder="Ej: Moisés Aponte")
        with c2:
            cliente = st.text_input("Nombre del cliente", value=st.session_state.nombre_cliente, placeholder="Ej: Ana Pérez")
        with c3:
            objetivo = st.text_input("Objetivo (1 línea)", value=st.session_state.objetivo_sesion, placeholder="Ej: Recuperar rutina de sueño")
        with c4:
            nivel = st.selectbox("Nivel", ["Nuevo", "En proceso", "Avanzado"],
                                 index=["Nuevo","En proceso","Avanzado"].index(st.session_state.nivel_cliente))
        ok = st.form_submit_button("Guardar ficha", type="primary", use_container_width=True)
        if ok:
            st.session_state.nombre_coach = coach.strip()
            st.session_state.nombre_cliente = cliente.strip()
            st.session_state.objetivo_sesion = objetivo.strip()
            st.session_state.nivel_cliente = nivel
            st.toast("Ficha guardada ✅", icon="🗂️")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.info("Consejo operativo: si el objetivo está vago, el Copiloto lo redefine en 1 línea y se acabó la charla circular.")

# -------------------------
# TAB 2: RUEDA
# -------------------------
with tab2:
    st.subheader("2) Rueda (input rápido + gráfico)")

    colA, colB = st.columns([1.2, 1])

    with colA:
        area_sel = st.selectbox("Área a evaluar", list(ruedas_data.keys()), index=list(ruedas_data.keys()).index(st.session_state.area_sel))
        st.session_state.area_sel = area_sel

        vectores = ruedas_data[area_sel]

        with st.form("rueda_form", clear_on_submit=False):
            st.caption("Puntuación 1–10. Mantén ritmo: precisión > explicación.")
            valores = []
            for v in vectores:
                valores.append(st.slider(v, 1, 10, 5, key=f"s_{area_sel}_{v}"))
            gen = st.form_submit_button("Guardar rueda", type="primary", use_container_width=True)

        if gen:
            st.session_state.datos_rueda = {"area": area_sel, "vectores": vectores, "valores": valores}
            st.toast("Rueda guardada ✅", icon="🎡")

    with colB:
        if st.session_state.datos_rueda:
            rueda = st.session_state.datos_rueda
            vectores = rueda["vectores"]
            valores = rueda["valores"]

            N = len(vectores)
            angulos = [n / float(N) * 2 * np.pi for n in range(N)]
            fig, ax = plt.subplots(figsize=(6.4, 6.4), subplot_kw=dict(polar=True))
            ax.set_theta_offset(np.pi / 2)
            ax.set_theta_direction(-1)
            plt.xticks(angulos, vectores, size=9, weight="bold")
            ax.plot(angulos + [angulos[0]], valores + [valores[0]], linewidth=2)
            ax.fill(angulos + [angulos[0]], valores + [valores[0]], alpha=0.18)
            st.pyplot(fig, use_container_width=True)
        else:
            st.markdown("<div class='h-card'>Aún no hay rueda guardada.</div>", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    if st.session_state.datos_rueda:
        df = pd.DataFrame(
            {"Vector": st.session_state.datos_rueda["vectores"], "Puntuación": st.session_state.datos_rueda["valores"]}
        ).sort_values("Puntuación")
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Guarda la rueda para ver el resumen.")

# -------------------------
# TAB 3: HIPÓTESIS IA
# -------------------------
with tab3:
    st.subheader("3) Hipótesis conductual (IA) — salida para dirigir la sesión")
    st.caption("Esto no es ‘análisis bonito’. Es: patrón → cuello de botella → autoengaño → prueba 7 días.")

    if not st.session_state.datos_rueda:
        st.warning("Primero guarda una rueda en el Tab 2.")
    else:
        c1, c2 = st.columns([1, 1])
        with c1:
            if st.button("🤖 Generar / Regenerar hipótesis", use_container_width=True, type="primary", disabled=not has_api_key()):
                with st.spinner("Analizando patrón..."):
                    model = get_model()
                    rueda = st.session_state.datos_rueda
                    puntuaciones = list(zip(rueda["vectores"], rueda["valores"]))

                    prompt_auto = f"""
Eres Director de Diagnóstico conductual. No motivas. No das teoría.

Cliente: {st.session_state.nombre_cliente or "No indicado"}
Objetivo declarado (si existe): {st.session_state.objetivo_sesion or "No indicado"}
Área: {rueda["area"]}
Vectores y puntuaciones: {puntuaciones}

REGLAS DURAS
- No repitas puntuaciones.
- Máx 170 palabras.
- Bullets, sin introducción.
- Cada bullet = afirmación + conducta observable + coste.
- OBLIGATORIO: 1 contradicción (lo que dice querer vs lo que sus hábitos muestran) y 1 trade-off (qué prioriza en silencio).

ENTREGA (en este orden)
- Patrón dominante (1 línea)
- Cuello de botella (NO el más bajo) + por qué arrastra otros
- Mecanismo de autoengaño (conducta semanal observable)
- Prueba 7 días (≤20 min/día, métrica binaria)
- Coste oculto (dinero/energía/relación/tiempo)
- Pregunta de quiebre (corta y verificable)
"""
                    resp = model.generate_content(prompt_auto)
                    st.session_state.diagnostico_generado = resp.text.strip()
                    st.toast("Hipótesis generada ✅", icon="🧠")

        with c2:
            if st.session_state.diagnostico_generado:
                st.success("Lista para usar en sesión.")
            else:
                st.info("Genera la hipótesis para tener guion base.")

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(st.session_state.diagnostico_generado or "—")

# -------------------------
# TAB 4: VAK 24
# -------------------------
with tab4:
    st.subheader("4) VAK 24 (guiado, sin ambigüedad)")
    st.caption("El cliente elige lo que más se le parece. Tú solo pides ejemplos si duda.")

    total = {"V": 0, "A": 0, "C": 0}

    with st.form("vak_form", clear_on_submit=False):
        for idx, item in enumerate(VAK_ITEMS):
            st.markdown("<div class='h-card'>", unsafe_allow_html=True)
            st.markdown(f"**{idx+1}. {item['titulo']}**")
            st.write(item["escena"])

            choice = st.radio(
                "Elige la opción que más se parece a ti:",
                options=["V", "A", "C"],
                format_func=lambda x: {"V": "Visual", "A": "Auditivo", "C": "Cinestésico"}[x],
                key=f"vak_{idx}",
                horizontal=True,
            )

            st.caption(
                {
                    "V": f"🖼️ {item['V']}",
                    "A": f"🎧 {item['A']}",
                    "C": f"🧠 {item['C']}",
                }[choice]
            )
            st.markdown("</div>", unsafe_allow_html=True)

            total[choice] += 1

        guardar = st.form_submit_button("Guardar perfil VAK", type="primary", use_container_width=True)

    if guardar:
        st.session_state.puntos_vak = total
        pred = max(total, key=total.get)
        mapa = {"V": "Visual", "A": "Auditivo", "C": "Cinestésico"}
        st.success(f"Perfil guardado ✅ Predominante: **{mapa[pred]}**")
        st.bar_chart(pd.DataFrame(total.items(), columns=["Canal", "Puntos"]).set_index("Canal"))

# -------------------------
# TAB 5: COPILOTO + PDF
# -------------------------
with tab5:
    st.subheader("5) Copiloto IA (guion en vivo) + Export PDF")
    st.caption("La IA te da: qué decir, qué preguntar, qué escuchar y qué tarea dejar. Tú llevas el control.")

    if not st.session_state.datos_rueda:
        st.warning("Guarda la rueda para activar el Copiloto (Tab 2).")
    else:
        # Historial de chat
        for msg in st.session_state.chat_hist:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Input chat
        user_input = st.chat_input("Pega aquí lo que el cliente acaba de decir (1–3 frases)…")

        if user_input:
            st.session_state.chat_hist.append({"role": "user", "content": user_input})

            if not has_api_key():
                st.session_state.chat_hist.append(
                    {"role": "assistant", "content": "⚠️ Falta `GEMINI_API_KEY` en Secrets. No puedo generar el siguiente paso."}
                )
                st.rerun()

            with st.spinner("Generando la siguiente jugada..."):
                model = get_model()
                rueda = st.session_state.datos_rueda
                puntuaciones = list(zip(rueda["vectores"], rueda["valores"]))
                diagnostico = st.session_state.diagnostico_generado or "No disponible"

                vak = st.session_state.puntos_vak or {"V": 0, "A": 0, "C": 0}
                pred = max(vak, key=vak.get) if any(vak.values()) else "V"
                mapa = {"V": "Visual", "A": "Auditivo", "C": "Cinestésico"}
                predominancia = mapa.get(pred, "Visual")

                prompt_copiloto = f"""
Eres Copiloto de Sesión GROW+ (coach estratégico). Respondes como guion práctico para el coach.
Tu objetivo: avanzar la sesión hoy, no hablar bonito.

CONTEXTO
Coach: {st.session_state.nombre_coach or "No indicado"}
Cliente: {st.session_state.nombre_cliente or "No indicado"}
Objetivo declarado: {st.session_state.objetivo_sesion or "No indicado"}
Área rueda: {rueda["area"]}
Puntuaciones: {puntuaciones}
Hipótesis previa (si existe): {diagnostico}
Canal predominante: {predominancia}
Última frase del cliente: {user_input}

REGLAS
- Directo, operativo, sin discursos.
- Máx 190 palabras.
- Usa predicados del canal {predominancia}.
- Si el objetivo está vago, REDEFINE en 1 línea primero.

SALIDA (bullets, en este orden exacto)
1) 🎯 DESAFÍO REDEFINIDO (1 línea)
2) 🗣️ COACH DICE (literal, 1–2 frases)
3) ❓ PREGUNTA SIGUIENTE (1 sola)
4) 🔁 SI RESPONDE “EVITA/DEPENDE” → repregunta exacta (1 sola)
5) ✅ TAREA 7 DÍAS (≤20 min, binaria, SMART) + fricción (qué eliminar)
6) ⚠️ SEÑAL DE AUTOENGAÑO (1 línea)
"""
                resp = model.generate_content(prompt_copiloto)
                assistant_text = resp.text.strip()

            st.session_state.chat_hist.append({"role": "assistant", "content": assistant_text})
            st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)

    c1, c2 = st.columns([1, 1])
    with c1:
        st.subheader("Descarga PDF (registro completo)")
        st.caption("Incluye ficha, rueda, hipótesis, VAK y chat del copiloto.")
        pdf_bytes = build_pdf_bytes()
        file_name = f"registro_{(st.session_state.nombre_cliente or 'cliente').replace(' ', '_')}.pdf"
        st.download_button(
            "⬇️ Descargar registro (PDF)",
            data=pdf_bytes,
            file_name=file_name,
            mime="application/pdf",
            use_container_width=True,
            type="primary",
        )

    with c2:
        st.subheader("Export rápido (TXT)")
        export_text = f"""BeCoach — Registro de Sesión
Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}

Coach: {st.session_state.nombre_coach}
Cliente: {st.session_state.nombre_cliente}
Objetivo: {st.session_state.objetivo_sesion}
Nivel: {st.session_state.nivel_cliente}

RUEDA: {st.session_state.datos_rueda}

HIPÓTESIS:
{st.session_state.diagnostico_generado}

VAK: {st.session_state.puntos_vak}

CHAT:
""" + "\n\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.chat_hist])

        st.download_button(
            "⬇️ Descargar resumen (TXT)",
            data=export_text.encode("utf-8"),
            file_name=f"sesion_{(st.session_state.nombre_cliente or 'cliente').replace(' ', '_')}.txt",
            mime="text/plain",
            use_container_width=True,
        )
