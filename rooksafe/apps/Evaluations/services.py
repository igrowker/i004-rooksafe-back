from .models import Evaluations

def calcular_puntaje_y_nivel(respuestas_usuario):

    # calculo el puntaje sumando todos los valores
    puntaje = sum(respuestas_usuario)
    total_preguntas = len(respuestas_usuario)
    
    # calculo el porcentaje del puntaje sobre el máximo posible (asumimos 10 como puntaje máximo)
    max_puntaje = total_preguntas * 10
    porcentaje_aciertos = (puntaje / max_puntaje) * 100

    # vemos el nivel de riesgo
    if porcentaje_aciertos >= 80:
        nivel_riesgo = "Agresivo"
    elif porcentaje_aciertos >= 45:
        nivel_riesgo = "Moderado"
    else:
        nivel_riesgo = "Conservador"

    return puntaje, nivel_riesgo


def crear_evaluacion(user, trader_name, puntaje, nivel_riesgo, total_preguntas):
    
    # creo y guardo el objeto Evaluations
    evaluacion = Evaluations.objects.create(
        user=user,
        trader_name=trader_name,
        risk_level=nivel_riesgo,
    )
    
    return evaluacion

def obtener_evaluaciones(trader_name=None):
    # si le pasamos 'trader_name', filtramos 
    if trader_name:
        evaluaciones = Evaluations.objects.filter(trader_name__icontains=trader_name)
    else:
        # caso contrario devolvemos todas las evaluaciones
        evaluaciones = Evaluations.objects.all()
    
    return evaluaciones
