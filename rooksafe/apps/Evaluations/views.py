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

from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.sessions.models import Session
from .services import calcular_puntaje_y_nivel, crear_evaluacion

class EvaluacionView(APIView):
    
    def post(self, request):

        #se espera un json con el puntaje y con el campo "ultima_ventana: True o False"

        # las respuestas del usuario de la solicitud
        respuestas_usuario = request.data.get("respuestas")
        ultima_ventana = request.data.get("ultima_ventana", False)
        
        # el nombre del trader
        trader_name = request.user.username  

        # si es la primera ventana, inicializamos la sesión si es necesario
        if "respuestas" not in request.session:
            request.session["respuestas"] = []

        # acumulamos las respuestas del usuario en la sesión
        request.session["respuestas"].extend(respuestas_usuario)
        request.session.modified = True 

        # si es la última ventana, calculamos el puntaje
        if ultima_ventana:
            
            # calcular el puntaje y el nivel de riesgo
            puntaje, nivel_riesgo = calcular_puntaje_y_nivel(request.session["respuestas"])

            evaluacion = crear_evaluacion(
                user=request.user,
                trader_name=trader_name,
                puntaje=puntaje,
                nivel_riesgo=nivel_riesgo,
                total_preguntas=len(request.session["respuestas"])
            )
            
            del request.session["respuestas"]

            return Response({
                "nivel_riesgo": evaluacion.risk_level,
                "puntaje": evaluacion.details,
                "trader_name": evaluacion.trader_name
            })

        # Si no es la última ventana, simplemente devolvemos un mensaje de éxito
        return Response({"message": "Respuestas recibidas correctamente."})
