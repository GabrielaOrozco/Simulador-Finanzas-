# -*- coding: utf-8 -*-
"""App etapa 3: trayectoria 2026-2030 como tercer módulo."""

from __future__ import annotations

import pandas as pd
import streamlit as st

try:
    import matplotlib.pyplot as plt
    from matplotlib.ticker import PercentFormatter
    MATPLOTLIB_OK = True
except Exception:
    MATPLOTLIB_OK = False

from modelo_modulo3 import (
    DEFAULT_SUPUESTOS_2026,
    calcular_modulo_3_trayectoria,
)
from parametros_modulo3 import PARAMS


st.set_page_config(page_title="Simulador de Finanzas Públicas", layout="wide")

ANIOS_MODULO_3 = [2026, 2027, 2028, 2029, 2030]
ANIOS_HIST = list(range(2015, 2026))
UNIDAD_MMDP = "Unidad: miles de millones de pesos (mmdp)"
UNIDAD_PCT_PIB = "Unidad: % del PIB"


@st.cache_data
def formatear_tabla(df: pd.DataFrame) -> pd.DataFrame:
    tabla = df.copy()
    for col in tabla.columns:
        if col != "Concepto":
            tabla[col] = tabla[col].map(lambda x: f"{float(x):,.1f}")
    return tabla


@st.cache_data
def formatear_tabla_pct(df: pd.DataFrame) -> pd.DataFrame:
    tabla = df.copy()
    for col in tabla.columns:
        if col != "Concepto":
            tabla[col] = tabla[col].map(lambda x: f"{float(x):,.1f}%")
    return tabla


def metrica(label: str, value: float) -> None:
    st.metric(label, f"{float(value):,.1f}")


def enriquecer_ingresos_para_tabla(ingresos: dict) -> dict:
    x = dict(ingresos)
    x["Gobierno Federal"] = float(x["Tributarios"]) + float(x["No tributarios"])
    x["OCPD y CFE"] = float(x["OCPD"]) + float(x["CFE"])
    return x


def construir_tabla_trayectoria_ingresos(trayectoria: dict) -> pd.DataFrame:
    filas = [
        ("PIB nominal", "PIB nominal"),
        ("Ingresos presupuestarios", "Ingresos presupuestarios"),
        ("Petroleros", "Petroleros"),
        ("  Gob.Federal (derechos y contrap)", "GF petroleros"),
        ("  Pemex", "Pemex"),
        ("No petroleros", "No petroleros"),
        ("  Gobierno Federal", "Gobierno Federal"),
        ("    Tributarios", "Tributarios"),
        ("    No tributarios", "No tributarios"),
        ("  OCPD y CFE", "OCPD y CFE"),
        ("    OCPD", "OCPD"),
        ("    CFE", "CFE"),
    ]

    data = {"Concepto": [etiqueta for etiqueta, _ in filas]}
    for anio in ANIOS_MODULO_3:
        ingresos = enriquecer_ingresos_para_tabla(trayectoria["ingresos_por_anio"][anio])
        data[str(anio)] = [float(ingresos[clave]) for _, clave in filas]
    return pd.DataFrame(data)


def construir_tabla_trayectoria_ingresos_pct(trayectoria: dict) -> pd.DataFrame:
    filas = [
        ("Ingresos presupuestarios", "Ingresos presupuestarios"),
        ("Petroleros", "Petroleros"),
        ("  Gob.Federal (derechos y contrap)", "GF petroleros"),
        ("  Pemex", "Pemex"),
        ("No petroleros", "No petroleros"),
        ("  Gobierno Federal", "Gobierno Federal"),
        ("    Tributarios", "Tributarios"),
        ("    No tributarios", "No tributarios"),
        ("  OCPD y CFE", "OCPD y CFE"),
        ("    OCPD", "OCPD"),
        ("    CFE", "CFE"),
    ]

    data = {"Concepto": [etiqueta for etiqueta, _ in filas]}
    for anio in ANIOS_MODULO_3:
        ingresos = enriquecer_ingresos_para_tabla(trayectoria["ingresos_por_anio"][anio])
        pib = float(trayectoria["ingresos_por_anio"][anio]["PIB nominal"])
        data[str(anio)] = [float(ingresos[clave]) / pib * 100 for _, clave in filas]
    return pd.DataFrame(data)


def construir_tabla_trayectoria_egresos(trayectoria: dict) -> pd.DataFrame:
    filas = [
        ("Gasto neto pagado", "Gasto neto pagado"),
        ("Programable pagado", "Programable pagado"),
        ("  Diferimiento de pagos", "Diferimiento de pagos"),
        ("  Gasto corriente", "Gasto corriente"),
        ("    Servicios personales", "Servicios personales"),
        ("    Gasto de operación", "Gasto de operación"),
        ("    Subsidios", "Subsidios"),
        ("  Pensiones y jubilaciones", "Pensiones y jubilaciones"),
        ("  Inversión", "Inversión total"),
        ("    Inversión física", "Inversión física"),
        ("    Inversión financiera", "Inversión financiera"),
        ("No programable", "No programable"),
        ("  Costo financiero", "Costo financiero"),
        ("  Participaciones", "Participaciones"),
        ("  Adefas", "Adefas"),
        ("Balance primario", "Balance primario"),
        ("Balance presupuestario", "Balance presupuestario"),
        ("NFFP", "NFFP"),
        ("RFSP", "RFSP"),
    ]

    data = {"Concepto": [etiqueta for etiqueta, _ in filas]}
    for anio in ANIOS_MODULO_3:
        egresos = trayectoria["egresos_por_anio"][anio]
        data[str(anio)] = [float(egresos[clave]) for _, clave in filas]
    return pd.DataFrame(data)


def construir_tabla_trayectoria_egresos_pct(trayectoria: dict) -> pd.DataFrame:
    filas = [
        ("Gasto neto pagado", "Gasto neto pagado"),
        ("Programable pagado", "Programable pagado"),
        ("  Diferimiento de pagos", "Diferimiento de pagos"),
        ("  Gasto corriente", "Gasto corriente"),
        ("    Servicios personales", "Servicios personales"),
        ("    Gasto de operación", "Gasto de operación"),
        ("    Subsidios", "Subsidios"),
        ("  Pensiones y jubilaciones", "Pensiones y jubilaciones"),
        ("  Inversión", "Inversión total"),
        ("    Inversión física", "Inversión física"),
        ("    Inversión financiera", "Inversión financiera"),
        ("No programable", "No programable"),
        ("  Costo financiero", "Costo financiero"),
        ("  Participaciones", "Participaciones"),
        ("  Adefas", "Adefas"),
        ("Balance primario", "Balance primario"),
        ("Balance presupuestario", "Balance presupuestario"),
        ("NFFP", "NFFP"),
        ("RFSP", "RFSP"),
    ]

    data = {"Concepto": [etiqueta for etiqueta, _ in filas]}
    for anio in ANIOS_MODULO_3:
        egresos = trayectoria["egresos_por_anio"][anio]
        pib = float(trayectoria["ingresos_por_anio"][anio]["PIB nominal"])
        data[str(anio)] = [float(egresos[clave]) / pib * 100 for _, clave in filas]
    return pd.DataFrame(data)


def construir_grafica_pct(
    historico: dict,
    proyeccion: dict,
    titulo: str,
    color_map: dict,
):
    if not MATPLOTLIB_OK:
        return None

    fig, ax = plt.subplots(figsize=(10, 4.5))
    for serie, historico_map in historico.items():
        color = color_map.get(serie)
        x_hist = sorted(historico_map.keys())
        y_hist = [historico_map[x] for x in x_hist]

        x_proj = sorted(proyeccion[serie].keys())
        y_proj = [proyeccion[serie][x] for x in x_proj]

        # Para evitar huecos visuales, la línea punteada arranca en el último
        # punto histórico y desde ahí conecta con 2026-2030.
        x_fut = [x_hist[-1]] + x_proj
        y_fut = [y_hist[-1]] + y_proj

        ax.plot(x_hist, y_hist, linewidth=2.2, linestyle='-', color=color, label=serie)
        ax.plot(x_fut, y_fut, linewidth=2.2, linestyle='--', color=color, label='_nolegend_')

    ax.set_title(titulo)
    ax.set_xlabel('')
    ax.set_ylabel('% del PIB')
    ax.set_xticks(list(range(2015, 2031)))
    ax.set_xticklabels([str(x) for x in range(2015, 2031)], rotation=45)
    ax.yaxis.set_major_formatter(PercentFormatter(xmax=100, decimals=1))
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    return fig


COLOR_MAP_ING_GASTO = {
    "Ingresos presupuestarios": "#4a4a4a",
    "Gasto neto pagado": "#0b3d91",
}
COLOR_MAP_BAL_RFSP = {
    "Balance presupuestario": "#4a4a4a",
    "RFSP": "#0b3d91",
}
COLOR_MAP_PET_NO_PET = {
    "Petroleros": "#4a4a4a",
    "No petroleros": "#0b3d91",
}


st.title("Simulador de Finanzas Públicas")
st.caption("Etapa 3: trayectoria 2026-2030 como tercer módulo")

st.sidebar.header("Escenario 2026")
with st.sidebar.expander("Supuestos 2026", expanded=True):
    crecimiento_real_pct = st.number_input(
        "Crecimiento real del PIB (%)",
        value=DEFAULT_SUPUESTOS_2026["crecimiento_real"] * 100,
        step=0.001,
        format="%.3f",
    )
    deflactor = st.number_input(
        "Deflactor del PIB",
        value=DEFAULT_SUPUESTOS_2026["deflactor"],
        step=0.001,
        format="%.3f",
    )
    crecimiento_real = crecimiento_real_pct / 100
    crecimiento_nominal = (1 + crecimiento_real) * (1 + deflactor) - 1
    st.text_input(
        "Crecimiento nominal del PIB (%)",
        value=f"{crecimiento_nominal * 100:.2f}",
        disabled=True,
    )
    precio_petroleo = st.number_input(
        "Precio del petróleo (US$/b)",
        value=DEFAULT_SUPUESTOS_2026["precio_petroleo"],
        step=0.10,
        format="%.2f",
    )
    tipo_cambio = st.number_input(
        "Tipo de cambio (pesos/US$)",
        value=DEFAULT_SUPUESTOS_2026["tipo_cambio"],
        step=0.10,
        format="%.2f",
    )
    produccion_petrolera = st.number_input(
        "Producción petrolera (mbd)",
        value=DEFAULT_SUPUESTOS_2026["produccion_petrolera"],
        step=1.0,
        format="%.1f",
    )
    consumo_energia = st.number_input(
        "Consumo nacional de energía",
        value=DEFAULT_SUPUESTOS_2026["consumo_energia"],
        step=1.0,
        format="%.3f",
    )
    cetes_28_pct = st.number_input(
        "CETES a 28 días promedio (%)",
        value=DEFAULT_SUPUESTOS_2026["cetes_28"] * 100,
        step=0.10,
        format="%.2f",
    )
    tasa_fed_pct = st.number_input(
        "Tasa FED (%)",
        value=DEFAULT_SUPUESTOS_2026["tasa_fed"] * 100,
        step=0.10,
        format="%.2f",
    )
    cetes_28 = cetes_28_pct / 100
    tasa_fed = tasa_fed_pct / 100

with st.sidebar.expander("Parámetros del modelo", expanded=True):
    elasticidad_tributarios = st.number_input(
        "Elasticidad ingresos-PIB",
        value=float(PARAMS["elasticidad_tributarios"]),
        step=0.01,
        format="%.2f",
    )
    pct_no_tributarios_pib = st.number_input(
        "% no tributarios / PIB (2026)",
        value=float(PARAMS["pct_no_tributarios_pib"]),
        step=0.1,
        format="%.1f",
    )

trayectoria = calcular_modulo_3_trayectoria(
    crecimiento_real_2026=crecimiento_real,
    deflactor_2026=deflactor,
    precio_petroleo_2026=precio_petroleo,
    tipo_cambio_2026=tipo_cambio,
    produccion_petrolera_2026=produccion_petrolera,
    consumo_energia_2026=consumo_energia,
    cetes_2026=cetes_28,
    tasa_fed_2026=tasa_fed,
    elasticidad_tributarios=elasticidad_tributarios,
    pct_no_tributarios_pib_2026=pct_no_tributarios_pib,
)

resultados_ingresos_2026 = trayectoria["ingresos_por_anio"][2026]
resultados_egresos_2026 = trayectoria["egresos_por_anio"][2026]
tabla_ingresos_2026_2030 = construir_tabla_trayectoria_ingresos(trayectoria)
tabla_ingresos_pct_pib = construir_tabla_trayectoria_ingresos_pct(trayectoria)
tabla_egresos_2026_2030 = construir_tabla_trayectoria_egresos(trayectoria)
tabla_egresos_pct_pib = construir_tabla_trayectoria_egresos_pct(trayectoria)

anio_seleccionado = st.selectbox("Año de referencia para métricas", ANIOS_MODULO_3, index=1)
res_ing = trayectoria["ingresos_por_anio"][anio_seleccionado]
res_egr = trayectoria["egresos_por_anio"][anio_seleccionado]

tab1, tab2, tab3 = st.tabs(
    ["Escenario 2026", "Módulo 3 · Ingresos 2026-2030", "Módulo 3 · Egresos 2026-2030"]
)

with tab1:
    st.subheader("Resultados clave 2026")
    st.caption(UNIDAD_MMDP)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metrica("Ingresos presupuestarios", resultados_ingresos_2026["Ingresos presupuestarios"])
    with c2:
        metrica("Gasto neto pagado", resultados_egresos_2026["Gasto neto pagado"])
    with c3:
        metrica("Balance presupuestario", resultados_egresos_2026["Balance presupuestario"])
    with c4:
        metrica("RFSP", resultados_egresos_2026["RFSP"])

    c5, c6, c7, c8 = st.columns(4)
    with c5:
        metrica("Petroleros", resultados_ingresos_2026["Petroleros"])
    with c6:
        metrica("No petroleros", resultados_ingresos_2026["No petroleros"])
    with c7:
        metrica("Costo financiero", resultados_egresos_2026["Costo financiero"])
    with c8:
        metrica("PIB nominal", resultados_ingresos_2026["PIB nominal"])

    st.markdown("**Tabla base 2026 (mmdp)**")
    tabla_2026 = pd.concat(
        [
            trayectoria["tablas_ingresos"][2026].rename(columns={"Monto 2026": "Monto"}),
            trayectoria["tablas_egresos"][2026].rename(columns={"Monto 2026": "Monto"}),
        ],
        ignore_index=True,
    )
    st.dataframe(formatear_tabla(tabla_2026), use_container_width=True, hide_index=True)

    st.markdown("**Gráficas (% del PIB)**")
    st.caption(UNIDAD_PCT_PIB)
    if not MATPLOTLIB_OK:
        st.warning("Matplotlib no está disponible en este entorno. Instálalo para ver las gráficas.")
    else:
        proyectadas_pct = {
            "Ingresos presupuestarios": {
                a: trayectoria["ingresos_por_anio"][a]["Ingresos presupuestarios"]
                / trayectoria["ingresos_por_anio"][a]["PIB nominal"]
                * 100
                for a in ANIOS_MODULO_3
            },
            "Gasto neto pagado": {
                a: trayectoria["egresos_por_anio"][a]["Gasto neto pagado"]
                / trayectoria["ingresos_por_anio"][a]["PIB nominal"]
                * 100
                for a in ANIOS_MODULO_3
            },
            "Balance presupuestario": {
                a: trayectoria["egresos_por_anio"][a]["Balance presupuestario"]
                / trayectoria["ingresos_por_anio"][a]["PIB nominal"]
                * 100
                for a in ANIOS_MODULO_3
            },
            "RFSP": {
                a: trayectoria["egresos_por_anio"][a]["RFSP"]
                / trayectoria["ingresos_por_anio"][a]["PIB nominal"]
                * 100
                for a in ANIOS_MODULO_3
            },
            "Petroleros": {
                a: trayectoria["ingresos_por_anio"][a]["Petroleros"]
                / trayectoria["ingresos_por_anio"][a]["PIB nominal"]
                * 100
                for a in ANIOS_MODULO_3
            },
            "No petroleros": {
                a: trayectoria["ingresos_por_anio"][a]["No petroleros"]
                / trayectoria["ingresos_por_anio"][a]["PIB nominal"]
                * 100
                for a in ANIOS_MODULO_3
            },
        }

        fig1 = construir_grafica_pct(
            historico={
                "Ingresos presupuestarios": PARAMS["historico_pct_pib"]["Ingresos presupuestarios"],
                "Gasto neto pagado": PARAMS["historico_pct_pib"]["Gasto neto pagado"],
            },
            proyeccion={
                "Ingresos presupuestarios": proyectadas_pct["Ingresos presupuestarios"],
                "Gasto neto pagado": proyectadas_pct["Gasto neto pagado"],
            },
            titulo="Ingresos y gasto neto pagado",
            color_map=COLOR_MAP_ING_GASTO,
        )
        st.pyplot(fig1)

        fig2 = construir_grafica_pct(
            historico={
                "Balance presupuestario": PARAMS["historico_pct_pib"]["Balance presupuestario"],
                "RFSP": PARAMS["historico_pct_pib"]["RFSP"],
            },
            proyeccion={
                "Balance presupuestario": proyectadas_pct["Balance presupuestario"],
                "RFSP": proyectadas_pct["RFSP"],
            },
            titulo="Balances",
            color_map=COLOR_MAP_BAL_RFSP,
        )
        st.pyplot(fig2)

        fig3 = construir_grafica_pct(
            historico={
                "Petroleros": PARAMS["historico_pct_pib"]["Petroleros"],
                "No petroleros": PARAMS["historico_pct_pib"]["No petroleros"],
            },
            proyeccion={
                "Petroleros": proyectadas_pct["Petroleros"],
                "No petroleros": proyectadas_pct["No petroleros"],
            },
            titulo="Composición de ingresos",
            color_map=COLOR_MAP_PET_NO_PET,
        )
        st.pyplot(fig3)

with tab2:
    st.subheader("Ingresos 2026-2030")
    st.caption(UNIDAD_MMDP)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metrica("Ingresos presupuestarios", res_ing["Ingresos presupuestarios"])
    with c2:
        metrica("Petroleros", res_ing["Petroleros"])
    with c3:
        metrica("No petroleros", res_ing["No petroleros"])
    with c4:
        metrica("PIB nominal", res_ing["PIB nominal"])

    st.markdown("**Trayectoria de ingresos 2026-2030 (mmdp)**")
    st.dataframe(formatear_tabla(tabla_ingresos_2026_2030), use_container_width=True, hide_index=True)

    st.markdown("**Trayectoria de ingresos 2026-2030 (% del PIB)**")
    st.caption(UNIDAD_PCT_PIB)
    st.dataframe(formatear_tabla_pct(tabla_ingresos_pct_pib), use_container_width=True, hide_index=True)

with tab3:
    st.subheader("Egresos 2026-2030")
    st.caption(UNIDAD_MMDP)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metrica("Gasto neto pagado", res_egr["Gasto neto pagado"])
    with c2:
        metrica("Programable pagado", res_egr["Programable pagado"])
    with c3:
        metrica("Costo financiero", res_egr["Costo financiero"])
    with c4:
        metrica("RFSP", res_egr["RFSP"])

    st.markdown("**Trayectoria de egresos 2026-2030 (mmdp)**")
    st.dataframe(formatear_tabla(tabla_egresos_2026_2030), use_container_width=True, hide_index=True)

    st.markdown("**Trayectoria de egresos 2026-2030 (% del PIB)**")
    st.caption(UNIDAD_PCT_PIB)
    st.dataframe(formatear_tabla_pct(tabla_egresos_pct_pib), use_container_width=True, hide_index=True)
