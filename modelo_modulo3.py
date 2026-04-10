# -*- coding: utf-8 -*-
"""Módulo 3: trayectoria 2026-2030."""

from __future__ import annotations

from math import exp, log
from typing import Dict, Optional

import pandas as pd

from parametros_modulo3 import PARAMS


DEFAULT_SUPUESTOS_2026 = {
    "crecimiento_real": 0.022619830085555126,
    "deflactor": 0.048,
    "precio_petroleo": 54.9,
    "tipo_cambio": 19.3,
    "produccion_petrolera": 1794.0,
    "consumo_energia": 10790.064,
    "cetes_28": float(PARAMS["cetes_28_base"][2026]),
    "tasa_fed": float(PARAMS["tasa_fed_base"][2026]),
}


def _valor_parametro(nombre: str, override: Optional[float] = None) -> float:
    return float(PARAMS[nombre] if override is None else override)


def calcular_pib_nominal_2026(crecimiento_real: float, deflactor: float) -> float:
    return float(PARAMS["pib_nominal_2025"]) * (1 + crecimiento_real) * (1 + deflactor)


def construir_pib_nominal_escenario(crecimiento_real_2026: float, deflactor_2026: float) -> Dict[int, float]:
    pib_base = {int(k): float(v) for k, v in PARAMS["pib_nominal_base"].items()}
    pib = dict(pib_base)
    pib[2026] = calcular_pib_nominal_2026(crecimiento_real_2026, deflactor_2026)

    for anio in range(2027, 2031):
        factor = float(pib_base[anio]) / float(pib_base[anio - 1])
        pib[anio] = pib[anio - 1] * factor
    return pib


def calcular_adefas_desde_pib(pib_nominal: float) -> float:
    return pib_nominal * float(PARAMS["pct_adefas_pib"])


def calcular_diferimiento_desde_pib(pib_nominal: float) -> float:
    return pib_nominal * float(PARAMS["pct_diferimiento_pagos_pib"])


def calcular_nffp_desde_pib(pib_nominal: float) -> float:
    return pib_nominal * float(PARAMS["pct_nffp_pib"])


def calcular_subsidios_base(anio: int) -> float:
    if anio == 2026:
        return float(PARAMS["subsidios_2026_base"])
    prioritarios = float(PARAMS["prioritarios_base_mmdp"][anio])
    participacion = float(PARAMS["prioritarios_subsidios_share"])
    return prioritarios / participacion


def calcular_costo_financiero(
    anio: int,
    pib_nominal: Dict[int, float],
    cetes_2026: Optional[float] = None,
    tasa_fed_2026: Optional[float] = None,
) -> float:
    anio_previo = anio - 1
    deuda_interna_previa = float(PARAMS["deuda_interna_pib_base"][anio_previo]) * float(pib_nominal[anio_previo])
    deuda_externa_previa = float(PARAMS["deuda_externa_pib_base"][anio_previo]) * float(pib_nominal[anio_previo])

    if anio == 2026:
        tasa_interna = float(PARAMS["cetes_28_base"][2026] if cetes_2026 is None else cetes_2026)
        tasa_externa = float(PARAMS["tasa_fed_base"][2026] if tasa_fed_2026 is None else tasa_fed_2026)
    else:
        tasa_interna = float(PARAMS["cetes_28_base"][anio])
        tasa_externa = float(PARAMS["tasa_fed_base"][anio])

    intereses_compensados = float(PARAMS["intereses_compensados_mmdp"])
    costo_interno = deuda_interna_previa * tasa_interna
    costo_externo = deuda_externa_previa * tasa_externa
    return costo_interno + costo_externo + intereses_compensados


def calcular_modulo_1_2026(
    crecimiento_real: float,
    deflactor: float,
    precio_petroleo: float,
    tipo_cambio: float,
    produccion_petrolera: float,
    consumo_energia: float,
    elasticidad_tributarios: Optional[float] = None,
    pct_no_tributarios_pib: Optional[float] = None,
    pemex_factor_ajuste: Optional[float] = None,
) -> Dict[str, float]:
    pib_nominal_2026 = calcular_pib_nominal_2026(crecimiento_real, deflactor)

    valor_hidro = produccion_petrolera * precio_petroleo * tipo_cambio
    gf_petroleros = exp(
        float(PARAMS["gf_intercepto"]) + float(PARAMS["gf_beta_valor_hidro"]) * log(valor_hidro)
    ) / 1000

    pemex = (
        exp(
            float(PARAMS["pemex_beta_produccion"]) * log(produccion_petrolera)
            + float(PARAMS["pemex_beta_precio"]) * log(precio_petroleo)
            + float(PARAMS["pemex_beta_tc"]) * log(tipo_cambio)
            + float(PARAMS["pemex_beta_dummy"]) * float(PARAMS["pemex_dummy"])
        )
        / 1_000_000
    ) * _valor_parametro("pemex_factor_ajuste", pemex_factor_ajuste)

    crecimiento_nominal_pib = (pib_nominal_2026 / float(PARAMS["pib_nominal_2025"])) - 1
    tributarios = float(PARAMS["tributarios_2025"]) * (
        1 + _valor_parametro("elasticidad_tributarios", elasticidad_tributarios) * crecimiento_nominal_pib
    )

    no_tributarios = pib_nominal_2026 * _valor_parametro("pct_no_tributarios_pib", pct_no_tributarios_pib) / 100

    imss = float(PARAMS["imss_2025"]) * (1 + float(PARAMS["tasa_imss"]))
    issste = float(PARAMS["issste_2025"]) * (1 + float(PARAMS["tasa_issste"]))
    ocpd = imss + issste

    cfe = exp(
        float(PARAMS["cfe_intercepto"])
        + float(PARAMS["cfe_beta_pib"]) * log(pib_nominal_2026)
        + float(PARAMS["cfe_beta_consumo"]) * log(consumo_energia)
    )

    petroleros = gf_petroleros + pemex
    no_petroleros = tributarios + no_tributarios + ocpd + cfe
    ingresos_presupuestarios = petroleros + no_petroleros

    return {
        "PIB nominal": pib_nominal_2026,
        "GF petroleros": gf_petroleros,
        "Pemex": pemex,
        "Petroleros": petroleros,
        "Tributarios": tributarios,
        "No tributarios": no_tributarios,
        "OCPD": ocpd,
        "CFE": cfe,
        "No petroleros": no_petroleros,
        "Ingresos presupuestarios": ingresos_presupuestarios,
        "IMSS": imss,
        "ISSSTE": issste,
    }


def calcular_modulo_2_2026(
    ingresos_presupuestarios: float,
    pib_nominal_2026: float,
    tributarios_2026: float,
    cetes_2026: Optional[float] = None,
    tasa_fed_2026: Optional[float] = None,
) -> Dict[str, float]:
    servicios_personales = float(PARAMS["servicios_personales_2025e"]) * (1 + float(PARAMS["tasa_servicios_personales"]))
    gasto_operacion = float(PARAMS["gasto_operacion_2025e"]) * (1 + float(PARAMS["tasa_gasto_operacion"]))
    subsidios = calcular_subsidios_base(2026)
    gasto_corriente = servicios_personales + gasto_operacion + subsidios

    pensiones = float(PARAMS["pensiones_2025e"]) * (1 + float(PARAMS["crecimiento_pensiones_por_anio"][2026]))
    inversion_fisica = float(PARAMS["inversion_fisica_base"][2026])
    inversion_financiera = float(PARAMS["inversion_financiera_base"][2026])
    inversion_total = inversion_fisica + inversion_financiera

    diferimiento_pagos = calcular_diferimiento_desde_pib(pib_nominal_2026)
    programable_pagado = gasto_corriente + pensiones + inversion_total + diferimiento_pagos

    pib_para_cf = {2025: float(PARAMS["pib_nominal_base"][2025]), 2026: pib_nominal_2026}
    costo_financiero = calcular_costo_financiero(2026, pib_para_cf, cetes_2026, tasa_fed_2026)
    participaciones = tributarios_2026 * float(PARAMS["share_participaciones_tributarios"])
    adefas = calcular_adefas_desde_pib(pib_nominal_2026)
    no_programable = costo_financiero + participaciones + adefas

    gasto_neto_pagado = programable_pagado + no_programable
    balance_presupuestario = ingresos_presupuestarios - gasto_neto_pagado
    balance_primario = balance_presupuestario + costo_financiero
    nffp = calcular_nffp_desde_pib(pib_nominal_2026)
    rfsp = balance_presupuestario + nffp

    return {
        "Servicios personales": servicios_personales,
        "Gasto de operación": gasto_operacion,
        "Subsidios": subsidios,
        "Gasto corriente": gasto_corriente,
        "Pensiones y jubilaciones": pensiones,
        "Inversión física": inversion_fisica,
        "Inversión financiera": inversion_financiera,
        "Inversión total": inversion_total,
        "Diferimiento de pagos": diferimiento_pagos,
        "Programable pagado": programable_pagado,
        "Costo financiero": costo_financiero,
        "Participaciones": participaciones,
        "Adefas": adefas,
        "No programable": no_programable,
        "Gasto neto pagado": gasto_neto_pagado,
        "Balance presupuestario": balance_presupuestario,
        "Balance primario": balance_primario,
        "NFFP": nffp,
        "RFSP": rfsp,
    }


def calcular_ingresos_por_anio(
    anio: int,
    pib_nominal: Dict[int, float],
    supuestos_macro: Dict[int, Dict[str, float]],
    tributarios_previos: float,
    imss_previos: float,
    issste_previos: float,
    elasticidad_tributarios: Optional[float] = None,
    pct_no_tributarios_pib_2026: Optional[float] = None,
    pemex_factor_ajuste: Optional[float] = None,
) -> Dict[str, float]:
    pib_anio = float(pib_nominal[anio])
    sup = supuestos_macro[anio]

    valor_hidro = sup["produccion_petrolera"] * sup["precio_petroleo"] * sup["tipo_cambio"]
    gf_petroleros = exp(
        float(PARAMS["gf_intercepto"]) + float(PARAMS["gf_beta_valor_hidro"]) * log(valor_hidro)
    ) / 1000

    pemex = (
        exp(
            float(PARAMS["pemex_beta_produccion"]) * log(sup["produccion_petrolera"])
            + float(PARAMS["pemex_beta_precio"]) * log(sup["precio_petroleo"])
            + float(PARAMS["pemex_beta_tc"]) * log(sup["tipo_cambio"])
            + float(PARAMS["pemex_beta_dummy"]) * float(PARAMS["pemex_dummy"])
        )
        / 1_000_000
    ) * _valor_parametro("pemex_factor_ajuste", pemex_factor_ajuste)

    crecimiento_nominal_pib = (pib_anio / float(pib_nominal[anio - 1])) - 1
    tributarios = tributarios_previos * (
        1 + _valor_parametro("elasticidad_tributarios", elasticidad_tributarios) * crecimiento_nominal_pib
    )

    if anio == 2026:
        pct_no_tributarios = _valor_parametro("pct_no_tributarios_pib", pct_no_tributarios_pib_2026)
    else:
        pct_no_tributarios = float(PARAMS["pct_no_tributarios_pib_por_anio"][anio])
    no_tributarios = pib_anio * pct_no_tributarios / 100

    imss = imss_previos * (1 + float(PARAMS["tasa_imss"]))
    issste = issste_previos * (1 + float(PARAMS["tasa_issste"]))
    ocpd = imss + issste

    cfe = exp(
        float(PARAMS["cfe_intercepto"])
        + float(PARAMS["cfe_beta_pib"]) * log(pib_anio)
        + float(PARAMS["cfe_beta_consumo"]) * log(sup["consumo_energia"])
    )

    petroleros = gf_petroleros + pemex
    no_petroleros = tributarios + no_tributarios + ocpd + cfe
    ingresos_presupuestarios = petroleros + no_petroleros

    return {
        "PIB nominal": pib_anio,
        "GF petroleros": gf_petroleros,
        "Pemex": pemex,
        "Petroleros": petroleros,
        "Tributarios": tributarios,
        "No tributarios": no_tributarios,
        "OCPD": ocpd,
        "CFE": cfe,
        "No petroleros": no_petroleros,
        "Ingresos presupuestarios": ingresos_presupuestarios,
        "IMSS": imss,
        "ISSSTE": issste,
    }


def calcular_egresos_por_anio(
    anio: int,
    ingresos_presupuestarios: float,
    pib_nominal: Dict[int, float],
    tributarios_anio: float,
    servicios_previos: float,
    operacion_previos: float,
    pensiones_previas: float,
    cetes_2026: Optional[float] = None,
    tasa_fed_2026: Optional[float] = None,
) -> Dict[str, float]:
    pib_nominal_anio = float(pib_nominal[anio])

    servicios_personales = servicios_previos * (1 + float(PARAMS["tasa_servicios_personales"]))
    gasto_operacion = operacion_previos * (1 + float(PARAMS["tasa_gasto_operacion"]))
    subsidios = calcular_subsidios_base(anio)
    gasto_corriente = servicios_personales + gasto_operacion + subsidios

    pensiones = pensiones_previas * (1 + float(PARAMS["crecimiento_pensiones_por_anio"][anio]))
    inversion_fisica = float(PARAMS["inversion_fisica_base"][anio])
    inversion_financiera = float(PARAMS["inversion_financiera_base"][anio])
    inversion_total = inversion_fisica + inversion_financiera

    diferimiento_pagos = calcular_diferimiento_desde_pib(pib_nominal_anio)
    programable_pagado = gasto_corriente + pensiones + inversion_total + diferimiento_pagos

    costo_financiero = calcular_costo_financiero(anio, pib_nominal, cetes_2026, tasa_fed_2026)
    participaciones = tributarios_anio * float(PARAMS["share_participaciones_tributarios"])
    adefas = calcular_adefas_desde_pib(pib_nominal_anio)
    no_programable = costo_financiero + participaciones + adefas

    gasto_neto_pagado = programable_pagado + no_programable
    balance_presupuestario = ingresos_presupuestarios - gasto_neto_pagado
    balance_primario = balance_presupuestario + costo_financiero
    nffp = calcular_nffp_desde_pib(pib_nominal_anio)
    rfsp = balance_presupuestario + nffp

    return {
        "Servicios personales": servicios_personales,
        "Gasto de operación": gasto_operacion,
        "Subsidios": subsidios,
        "Gasto corriente": gasto_corriente,
        "Pensiones y jubilaciones": pensiones,
        "Inversión física": inversion_fisica,
        "Inversión financiera": inversion_financiera,
        "Inversión total": inversion_total,
        "Diferimiento de pagos": diferimiento_pagos,
        "Programable pagado": programable_pagado,
        "Costo financiero": costo_financiero,
        "Participaciones": participaciones,
        "Adefas": adefas,
        "No programable": no_programable,
        "Gasto neto pagado": gasto_neto_pagado,
        "Balance presupuestario": balance_presupuestario,
        "Balance primario": balance_primario,
        "NFFP": nffp,
        "RFSP": rfsp,
    }


def construir_tabla_ingresos(anio: int, ingresos: Dict[str, float]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Concepto": [
                "PIB nominal",
                "Ingresos presupuestarios",
                "Petroleros",
                "  Gob.Federal (derechos y contrap)",
                "  Pemex",
                "No petroleros",
                "  Tributarios",
                "  No tributarios",
                "  OCPD y CFE",
                "    OCPD",
                "    CFE",
            ],
            f"Monto {anio}": [
                ingresos["PIB nominal"],
                ingresos["Ingresos presupuestarios"],
                ingresos["Petroleros"],
                ingresos["GF petroleros"],
                ingresos["Pemex"],
                ingresos["No petroleros"],
                ingresos["Tributarios"],
                ingresos["No tributarios"],
                ingresos["OCPD"] + ingresos["CFE"],
                ingresos["OCPD"],
                ingresos["CFE"],
            ],
        }
    )


def construir_tabla_egresos(anio: int, egresos: Dict[str, float]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Concepto": [
                "Gasto neto pagado",
                "Programable pagado",
                "  Diferimiento de pagos",
                "  Gasto corriente",
                "    Servicios personales",
                "    Gasto de operación",
                "    Subsidios",
                "  Pensiones y jubilaciones",
                "  Inversión",
                "    Inversión física",
                "    Inversión financiera",
                "No programable",
                "  Costo financiero",
                "  Participaciones",
                "  Adefas",
                "Balance primario",
                "Balance presupuestario",
                "NFFP",
                "RFSP",
            ],
            f"Monto {anio}": [
                egresos["Gasto neto pagado"],
                egresos["Programable pagado"],
                egresos["Diferimiento de pagos"],
                egresos["Gasto corriente"],
                egresos["Servicios personales"],
                egresos["Gasto de operación"],
                egresos["Subsidios"],
                egresos["Pensiones y jubilaciones"],
                egresos["Inversión total"],
                egresos["Inversión física"],
                egresos["Inversión financiera"],
                egresos["No programable"],
                egresos["Costo financiero"],
                egresos["Participaciones"],
                egresos["Adefas"],
                egresos["Balance primario"],
                egresos["Balance presupuestario"],
                egresos["NFFP"],
                egresos["RFSP"],
            ],
        }
    )


def calcular_modulo_3_trayectoria(
    crecimiento_real_2026: float,
    deflactor_2026: float,
    precio_petroleo_2026: float,
    tipo_cambio_2026: float,
    produccion_petrolera_2026: float,
    consumo_energia_2026: float,
    cetes_2026: Optional[float] = None,
    tasa_fed_2026: Optional[float] = None,
    elasticidad_tributarios: Optional[float] = None,
    pct_no_tributarios_pib_2026: Optional[float] = None,
    pemex_factor_ajuste: Optional[float] = None,
) -> Dict[str, object]:
    pib_nominal = construir_pib_nominal_escenario(crecimiento_real_2026, deflactor_2026)

    supuestos_macro = {
        int(anio): {k: float(v) for k, v in valores.items()}
        for anio, valores in PARAMS["supuestos_macro_base"].items()
    }
    supuestos_macro[2026] = {
        "produccion_petrolera": float(produccion_petrolera_2026),
        "precio_petroleo": float(precio_petroleo_2026),
        "tipo_cambio": float(tipo_cambio_2026),
        "consumo_energia": float(consumo_energia_2026),
    }

    ingresos_por_anio: Dict[int, Dict[str, float]] = {}
    egresos_por_anio: Dict[int, Dict[str, float]] = {}
    tablas_ingresos: Dict[int, pd.DataFrame] = {}
    tablas_egresos: Dict[int, pd.DataFrame] = {}

    tributarios_previos = float(PARAMS["tributarios_2025"])
    imss_previos = float(PARAMS["imss_2025"])
    issste_previos = float(PARAMS["issste_2025"])
    servicios_previos = float(PARAMS["servicios_personales_2025e"])
    operacion_previos = float(PARAMS["gasto_operacion_2025e"])
    pensiones_previas = float(PARAMS["pensiones_2025e"])

    for anio in range(2026, 2031):
        ingresos = calcular_ingresos_por_anio(
            anio=anio,
            pib_nominal=pib_nominal,
            supuestos_macro=supuestos_macro,
            tributarios_previos=tributarios_previos,
            imss_previos=imss_previos,
            issste_previos=issste_previos,
            elasticidad_tributarios=elasticidad_tributarios,
            pct_no_tributarios_pib_2026=pct_no_tributarios_pib_2026,
            pemex_factor_ajuste=pemex_factor_ajuste,
        )
        egresos = calcular_egresos_por_anio(
            anio=anio,
            ingresos_presupuestarios=ingresos["Ingresos presupuestarios"],
            pib_nominal=pib_nominal,
            tributarios_anio=ingresos["Tributarios"],
            servicios_previos=servicios_previos,
            operacion_previos=operacion_previos,
            pensiones_previas=pensiones_previas,
            cetes_2026=cetes_2026,
            tasa_fed_2026=tasa_fed_2026,
        )

        ingresos_por_anio[anio] = ingresos
        egresos_por_anio[anio] = egresos
        tablas_ingresos[anio] = construir_tabla_ingresos(anio, ingresos)
        tablas_egresos[anio] = construir_tabla_egresos(anio, egresos)

        tributarios_previos = ingresos["Tributarios"]
        imss_previos = ingresos["IMSS"]
        issste_previos = ingresos["ISSSTE"]
        servicios_previos = egresos["Servicios personales"]
        operacion_previos = egresos["Gasto de operación"]
        pensiones_previas = egresos["Pensiones y jubilaciones"]

    resumen_ingresos = pd.DataFrame(
        {
            "Año": list(range(2026, 2031)),
            "Ingresos presupuestarios": [ingresos_por_anio[a]["Ingresos presupuestarios"] for a in range(2026, 2031)],
            "Petroleros": [ingresos_por_anio[a]["Petroleros"] for a in range(2026, 2031)],
            "No petroleros": [ingresos_por_anio[a]["No petroleros"] for a in range(2026, 2031)],
        }
    )
    resumen_egresos = pd.DataFrame(
        {
            "Año": list(range(2026, 2031)),
            "Gasto neto pagado": [egresos_por_anio[a]["Gasto neto pagado"] for a in range(2026, 2031)],
            "Costo financiero": [egresos_por_anio[a]["Costo financiero"] for a in range(2026, 2031)],
            "RFSP": [egresos_por_anio[a]["RFSP"] for a in range(2026, 2031)],
        }
    )

    return {
        "pib_nominal": pib_nominal,
        "supuestos_macro": supuestos_macro,
        "ingresos_por_anio": ingresos_por_anio,
        "egresos_por_anio": egresos_por_anio,
        "tablas_ingresos": tablas_ingresos,
        "tablas_egresos": tablas_egresos,
        "resumen_ingresos": resumen_ingresos,
        "resumen_egresos": resumen_egresos,
    }
