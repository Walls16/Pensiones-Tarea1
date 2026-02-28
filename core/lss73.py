import pandas as pd

def calcular_pension_lss73(
    salario_diario,
    salario_minimo_diario,
    edad,
    semanas_cotizadas,
    conyuge=False
):
    """
    Modelo LSS 1973 matemáticamente limpio (sin redondeos intermedios).
    Solo se redondea al final para presentación.
    """

    # -----------------------------
    # 1. Grupo salarial (en veces SM)
    # -----------------------------
    grupo = salario_diario / salario_minimo_diario

    # -----------------------------
    # 2. Leer tabla cuantía básica
    # -----------------------------
    tabla = pd.read_csv("data/tabla_lss73_cuantia.csv")

    fila = tabla[
        (grupo >= tabla["limite_inferior"]) &
        (grupo < tabla["limite_superior"])
    ].iloc[0]

    porcentaje_base = fila["cuantia_basica_pct"] 
    incremento_pct = fila["incremento_anual_pct"] 

    # -----------------------------
    # 3. Cuantía básica anual
    # -----------------------------
    salario_anual = salario_diario * 365
    cuantia_base_anual = salario_anual * porcentaje_base

    # -----------------------------
    # 4. Incremento por semanas
    # -----------------------------
    if semanas_cotizadas > 500:
        anos_excedentes = (semanas_cotizadas - 500) / 52
    else:
        anos_excedentes = 0

    incremento_anual = cuantia_base_anual * incremento_pct * anos_excedentes

    pension_anual = cuantia_base_anual + incremento_anual

    # -----------------------------
    # 5. Factor por edad (Cesantía)
    # -----------------------------
    factores_edad = {
        60: 0.75,
        61: 0.80,
        62: 0.85,
        63: 0.90,
        64: 0.95,
        65: 1.00
    }

    if edad < 60:
        raise ValueError("Edad mínima para pensión: 60 años")

    factor_edad = factores_edad.get(edad, 1.00)

    pension_anual *= factor_edad

    # -----------------------------
    # 6. Asignación familiar
    # -----------------------------
    if conyuge:
        pension_anual *= 1.15
    else:
        pension_anual *= 1.15  # Soledad también es 15%

    # -----------------------------
    # 7. Convertir a diaria y mensual
    # -----------------------------
    pension_diaria = pension_anual / 365
    pension_mensual = pension_diaria * 30.4

    # -----------------------------
    # 8. Tasa de reemplazo
    # -----------------------------
    tasa_reemplazo = (pension_diaria / salario_diario) * 100

    # -----------------------------
    # 9. Redondeo final (presentación)
    # -----------------------------
    return {
        "pension_base_diaria": round(cuantia_base_anual / 365, 2),
        "pension_final_diaria": round(pension_diaria, 2),
        "pension_mensual": round(pension_mensual, 2),
        "tasa_reemplazo_pct": round(tasa_reemplazo, 2)
    }


def encontrar_semanas_para_tasa_objetivo(
    salario_diario,
    salario_minimo_diario,
    edad,
    tasa_objetivo,
    conyuge=False,
    semanas_min=500,
    semanas_max=3000,
    tolerancia=0.01
):
    """
    Encuentra el número de semanas necesarias para alcanzar
    una tasa de reemplazo objetivo bajo LSS 73.
    """

    low = semanas_min
    high = semanas_max

    while low <= high:
        mid = (low + high) // 2

        resultado = calcular_pension_lss73(
            salario_diario,
            salario_minimo_diario,
            edad,
            mid,
            conyuge
        )

        tasa_actual = resultado["tasa_reemplazo_pct"]

        if abs(tasa_actual - tasa_objetivo) < tolerancia:
            return {
                "semanas_necesarias": mid,
                "tasa_lograda": tasa_actual
            }

        if tasa_actual < tasa_objetivo:
            low = mid + 1
        else:
            high = mid - 1

    return {
        "semanas_necesarias": None,
        "mensaje": "No se pudo alcanzar la tasa objetivo en el rango dado."
    }

def generar_curva_tasa_vs_semanas(
    salario_diario,
    salario_minimo_diario,
    edad,
    conyuge=False,
    semanas_min=500,
    semanas_max=3000,
    paso=50
):
    """
    Genera lista de semanas y tasas correspondientes
    para graficar tasa de reemplazo vs semanas.
    """

    semanas_lista = []
    tasas_lista = []

    for semanas in range(semanas_min, semanas_max + 1, paso):
        resultado = calcular_pension_lss73(
            salario_diario,
            salario_minimo_diario,
            edad,
            semanas,
            conyuge
        )
        semanas_lista.append(semanas)
        tasas_lista.append(resultado["tasa_reemplazo_pct"])

    return semanas_lista, tasas_lista