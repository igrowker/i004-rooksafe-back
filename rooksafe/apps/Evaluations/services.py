from .models import Evaluations

def calcular_puntaje_y_nivel(respuestas_usuario):
    puntaje = 0
    total_preguntas = len(respuestas_usuario)
    
    # calcular puntaje sumando por cada respuesta correcta
    for respuesta in respuestas_usuario:
        if respuesta.get("correcta"):  # Esta es la respuesta esperada
            puntaje += 1

    # calculo de porcentaje
    porcentaje_aciertos = (puntaje / total_preguntas) * 100

    # determino nivel de riesgo
    if porcentaje_aciertos >= 80:
        nivel_riesgo = "avanzado"
    elif porcentaje_aciertos >= 45:
        nivel_riesgo = "intermedio"
    else:
        nivel_riesgo = "principiante"

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
