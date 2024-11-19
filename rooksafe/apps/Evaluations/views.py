from rest_framework.views import APIView
from rest_framework.response import Response
from .services import calcular_puntaje_y_nivel, crear_evaluacion, obtener_evaluaciones
from .serializers import EvaluationsSerializer

class EvaluacionView(APIView):

    def get(self, request):
        # Obtener el parámetro 'trader_name' de la solicitud (si se pasa)
        trader_name = request.query_params.get('trader_name', None)
        
        # Usar el servicio para obtener las evaluaciones
        evaluaciones = obtener_evaluaciones(trader_name)
        
        # Serializar los resultados
        serializer = EvaluationsSerializer(evaluaciones, many=True)
        
        return Response(serializer.data)

    def post(self, request):
        puntajes_usuario  = request.data.get("respuestas")

        trader_name = request.user.username  

        # llamo a calcular el porcentaje pasando las respuestas del usuario
        puntaje, nivel_riesgo = calcular_puntaje_y_nivel(puntajes_usuario)
        
        # creo la evaluacion 
        evaluacion = crear_evaluacion(
            user=request.user,
            trader_name=trader_name,
            puntaje=puntaje,
            nivel_riesgo=nivel_riesgo,
            total_preguntas=len(respuestas_usuario)
        )

        # doy una respuesta con los datos
        return Response({
            "nivel_riesgo": evaluacion.risk_level,
            "puntaje": evaluacion.details,
            "trader_name": evaluacion.trader_name
        })
