import pandas as pd
from core.loaders import load_table
# ==========================
# PARÁMETROS GENERALES
# ==========================

UMA_MENSUAL = 3566.22

# Cargar tabla ISR una sola vez
tabla_isr = load_table("isr_mensual_2026.csv")

# ======================================================
# FUNCIÓN ISR
# ======================================================

def calcular_isr_mensual(salario):

    fila = tabla_isr[
        (tabla_isr["limite_inferior"] <= salario) &
        (tabla_isr["limite_superior"] >= salario)
    ].iloc[0]

    limite_inf = fila["limite_inferior"]
    cuota_fija = fila["cuota_fija"]
    tasa = fila["tasa"]

    isr = cuota_fija + (salario - limite_inf) * tasa

    return isr


# ======================================================
# FUNCIÓN PRINCIPAL
# ======================================================

def calcular_contribuciones(sbc):

    trabajador = {}
    patron = {}
    gobierno = {}

    # ======================================================
    # PATRÓN
    # ======================================================

    patron["Riesgo de trabajo"] = {
        "base": sbc,
        "tasa": 0.019341,
        "monto": sbc * 0.019341
    }

    # Cuota fija (1 UMA para coincidir con Excel)
    patron["E y M - Cuota fija"] = {
        "base": UMA_MENSUAL,
        "tasa": 0.2040,
        "monto": UMA_MENSUAL * 0.2040
    }

    base_excedente = max(sbc - (3 * UMA_MENSUAL), 0)

    patron["E y M - Excedente"] = {
        "base": base_excedente,
        "tasa": 0.011,
        "monto": base_excedente * 0.011
    }

    patron["E y M - Dinero"] = {
        "base": sbc,
        "tasa": 0.007,
        "monto": sbc * 0.007
    }

    patron["E y M - Pensionados"] = {
        "base": sbc,
        "tasa": 0.0105,
        "monto": sbc * 0.0105
    }

    patron["Invalidez y Vida"] = {
        "base": sbc,
        "tasa": 0.0175,
        "monto": sbc * 0.0175
    }

    patron["Retiro"] = {
        "base": sbc,
        "tasa": 0.02,
        "monto": sbc * 0.02
    }

    patron["Cesantía y Vejez"] = {
        "base": sbc,
        "tasa": 0.07513,
        "monto": sbc * 0.07513
    }

    patron["Guarderías y Prestaciones Sociales"] = {
        "base": sbc,
        "tasa": 0.01,
        "monto": sbc * 0.01
    }

    patron["Infonavit"] = {
        "base": sbc,
        "tasa": 0.05,
        "monto": sbc * 0.05
    }

    # ======================================================
    # TRABAJADOR
    # ======================================================

    trabajador["E y M - Excedente"] = {
        "base": base_excedente,
        "tasa": 0.004,
        "monto": base_excedente * 0.004
    }

    trabajador["E y M - Dinero"] = {
        "base": sbc,
        "tasa": 0.0025,
        "monto": sbc * 0.0025
    }

    trabajador["E y M - Pensionados"] = {
        "base": sbc,
        "tasa": 0.00375,
        "monto": sbc * 0.00375
    }

    trabajador["Invalidez y Vida"] = {
        "base": sbc,
        "tasa": 0.00625,
        "monto": sbc * 0.00625
    }

    trabajador["Cesantía y Vejez"] = {
        "base": sbc,
        "tasa": 0.01125,
        "monto": sbc * 0.01125
    }

    # ==========================
    # ISR
    # ==========================

    isr = calcular_isr_mensual(sbc)

    trabajador["ISR"] = {
        "base": sbc,
        "tasa": isr / sbc if sbc > 0 else 0,
        "monto": isr
    }

    # ======================================================
    # GOBIERNO
    # ======================================================

    gobierno["E y M - Cuota fija"] = {
        "base": UMA_MENSUAL,
        "tasa": 0.1491,
        "monto": UMA_MENSUAL * 0.1491
    }

    gobierno["E y M - Dinero"] = {
        "base": sbc,
        "tasa": 0.0005,
        "monto": sbc * 0.0005
    }

    gobierno["E y M - Pensionados"] = {
        "base": sbc,
        "tasa": 0.00075,
        "monto": sbc * 0.00075
    }

    gobierno["Invalidez y Vida"] = {
        "base": sbc,
        "tasa": 0.00125,
        "monto": sbc * 0.00125
    }

    return {
        "trabajador": trabajador,
        "patron": patron,
        "gobierno": gobierno
    }