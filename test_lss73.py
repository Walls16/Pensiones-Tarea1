from core.lss73 import calcular_pension_lss73
from core.lss73 import encontrar_semanas_para_tasa_objetivo


resultado = encontrar_semanas_para_tasa_objetivo(
    salario_diario=2000,
    salario_minimo_diario=248.93,
    edad=65,
    tasa_objetivo=30,
    conyuge=True
)

print(resultado)