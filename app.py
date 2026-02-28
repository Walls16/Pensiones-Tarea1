import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from core.calculations import (
    calcular_contribuciones,
)

from core.pdf_generator import generar_pdf_contribuciones
from core.lss73 import (
    calcular_pension_lss73,
    encontrar_semanas_para_tasa_objetivo,
    generar_curva_tasa_vs_semanas
)

# -------------------------
# Configuración general
# -------------------------
st.set_page_config(
    page_title="Simulador de Contribuciones",
    layout="wide"
)

st.title("Simulador de Contribuciones")
st.markdown("Simulación de contribuciones")

# -------------------------
# Tabs
# -------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "Simulación individual",
    "Análisis por nivel de ingreso",
    "Régimen 1973 (Pensión)",
    "Metodología"
])

# ======================================================
# TAB 1 — SIMULACIÓN INDIVIDUAL
# ======================================================# ======================================================
# TAB 1 — SIMULACIÓN INDIVIDUAL
# ======================================================
with tab1:

    def plot_contribuciones_plotly(contribuciones):
        data = []

        for grupo in ["trabajador", "patron", "gobierno"]:
            conceptos = contribuciones[grupo]

            for concepto, info in conceptos.items():
                monto = info["monto"]
                if monto > 0:
                    data.append({
                        "Grupo": grupo.capitalize(),
                        "Concepto": concepto,
                        "Monto": monto
                    })

        if not data:
            return px.bar(title="No hay contribuciones para mostrar")

        df = pd.DataFrame(data)

        fig = px.bar(
            df,
            x="Grupo",
            y="Monto",
            color="Concepto",
            title="Distribución de contribuciones",
            labels={"Monto": "Monto mensual ($)"},
            color_discrete_sequence=px.colors.qualitative.Pastel
        )

        fig.update_layout(
            legend_title_text="Conceptos",
            hovermode="x unified"
        )

        fig.update_yaxes(tickprefix="$")

        return fig


    salario = st.number_input(
        "Salario Base de Cotización mensual (SBC)",
        min_value=0.0,
        step=100.0,
        format="%.2f"
    )

    if salario > 0:

        contribuciones = calcular_contribuciones(salario)

        trabajador = contribuciones["trabajador"]
        patron = contribuciones["patron"]
        gobierno = contribuciones["gobierno"]

        # Totales correctos
        total_trabajador = sum(v["monto"] for v in trabajador.values())
        total_patron = sum(v["monto"] for v in patron.values())
        total_gobierno = sum(v["monto"] for v in gobierno.values())

        salario_neto = salario - total_trabajador

        col1, col2, col3 = st.columns(3)

        # ======================
        # TRABAJADOR
        # ======================
        with col1:
            st.subheader("👤 Trabajador")

            for k, v in trabajador.items():
                st.write(f"{k}: ${v['monto']:,.2f}")

            st.divider()
            st.write(f"**Total trabajador:** ${total_trabajador:,.2f}")
            st.write(f"**% del SBC:** {total_trabajador / salario * 100:.2f}%")

        # ======================
        # PATRÓN
        # ======================
        with col2:
            st.subheader("🏢 Patrón")

            for k, v in patron.items():
                st.write(f"{k}: ${v['monto']:,.2f}")

            st.divider()
            st.write(f"**Total patrón:** ${total_patron:,.2f}")
            st.write(f"**% del SBC:** {total_patron / salario * 100:.2f}%")

        # ======================
        # GOBIERNO
        # ======================
        with col3:
            st.subheader("🏛️ Gobierno")

            for k, v in gobierno.items():
                st.write(f"{k}: ${v['monto']:,.2f}")

            st.divider()
            st.write(f"**Total gobierno:** ${total_gobierno:,.2f}")
            st.write(f"**% del SBC:** {total_gobierno / salario * 100:.2f}%")

        # ======================
        # GRÁFICA
        # ======================
        st.divider()
        st.subheader("📈 Distribución")

        fig = plot_contribuciones_plotly(contribuciones)
        st.plotly_chart(fig, use_container_width=True)

        # ======================
        # SALARIO
        # ======================
        st.write(f"**Salario bruto:** ${salario:,.2f}")
        st.write(f"**Salario neto estimado:** ${salario_neto:,.2f}")

        # ======================
        # PDF (si lo usas)
        # ======================
        pdf_buffer = generar_pdf_contribuciones(salario, contribuciones)

        st.download_button(
            label="Descargar recibo en PDF",
            data=pdf_buffer,
            file_name="recibo_contribuciones.pdf",
            mime="application/pdf"
        )

    else:
        st.info("Ingresa un salario mayor a cero.")

# ======================================================
# TAB 2 — ANÁLISIS POR NIVEL DE INGRESO
# ======================================================
# ======================================================
# TAB 2 — ANÁLISIS POR NIVEL DE INGRESO
# ======================================================
with tab2:

    st.subheader("📈 Contribuciones efectivas por nivel de ingreso")

    if salario <= 0:
        st.info("Primero ingresa un salario válido en la pestaña de simulación.")
    else:

        salarios = list(range(5_000, 100_001, 500))
        data = []

        for s in salarios:
            c = calcular_contribuciones(s)

            trabajador_dict = c["trabajador"]

            # Total trabajador correcto
            trabajador_sum = sum(v["monto"] for v in trabajador_dict.values())

            # ISR correcto (extraer monto del dict)
            isr = trabajador_dict["ISR"]["monto"]

            data.append({
                "Salario": s,
                "ISR Efectivo": (isr / s * 100),
                "Seguridad Social": ((trabajador_sum - isr) / s * 100),
                "Total Contribuciones": (trabajador_sum / s * 100)
            })

        df = pd.DataFrame(data)

        df_melted = df.melt(
            id_vars="Salario",
            var_name="Tipo",
            value_name="Porcentaje"
        )

        # Punto actual (salario ingresado)
        c_actual = calcular_contribuciones(salario)
        trabajador_actual = c_actual["trabajador"]

        total_t = sum(v["monto"] for v in trabajador_actual.values())
        isr_t = trabajador_actual["ISR"]["monto"]
        total_pct_actual = (total_t / salario) * 100

        fig = px.line(
            df_melted,
            x="Salario",
            y="Porcentaje",
            color="Tipo",
            title="Carga efectiva de ISR y seguridad social"
        )

        fig.update_layout(hovermode="x unified")

        fig.add_trace(go.Scatter(
            x=[salario],
            y=[total_pct_actual],
            mode="markers",
            name="Estás aquí",
            marker=dict(size=14, color="red", symbol="star")
        ))

        st.plotly_chart(fig, use_container_width=True)

# ======================================================
# TAB 3 — RÉGIMEN 1973
# ======================================================
with tab3:

    st.subheader("Cálculo de Pensión — LSS 1973")

    salario_diario = st.number_input("Salario diario", min_value=0.0, step=10.0)
    salario_minimo_diario = st.number_input("Salario mínimo diario", value=248.93)
    edad = st.slider("Edad", 60, 65, 65)
    semanas = st.number_input("Semanas cotizadas", min_value=500, step=50)
    conyuge = st.checkbox("¿Tiene cónyuge?")

    if salario_diario > 0:

        resultado = calcular_pension_lss73(
            salario_diario,
            salario_minimo_diario,
            edad,
            semanas,
            conyuge
        )

        st.metric("Pensión mensual estimada", f"${resultado['pension_mensual']:,.2f}")
        st.metric("Tasa de reemplazo", f"{resultado['tasa_reemplazo_pct']:.2f}%")

# ======================================================
# TAB 4 — METODOLOGÍA
# ======================================================
with tab4:
    st.markdown("""
    ### Metodología

    - LSS 1997 para contribuciones.
    - LSS 1973 para pensión.
    - Modelo matemático limpio sin redondeos intermedios.
    - Resultados con fines educativos.
    """)