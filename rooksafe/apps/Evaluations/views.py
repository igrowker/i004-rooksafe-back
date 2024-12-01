from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model

user = get_user_model()

LEVEL_MAPPING = {
    "básico": {
        "profile": "Conservador",
        "front_level": "Inicial",
        "description": [
            "Tenés mucha aversión al riesgo. Preferís inversiones más seguras.",
            "Buscás no sufrir pérdidas bajo ninguna circunstancia, o sufrir la menor pérdida posible.",
            "Tu foco no es generar una ganancia grande, sino limitar al máximo las pérdidas.",
            "Tu benchmark de rendimiento está por debajo del rendimiento promedio del mercado."
        ],
    },
    "intermedio": {
        "profile": "Equilibrado",
        "front_level": "Intermedio",
        "description": [
            "Buscás un poco más de rentabilidad.",
            "Resignás algo de seguridad por mayor rentabilidad.",
            "Intentás tener un portfolio balanceado, generar más ganancias, tomar mayores riesgos,",
            "pero no perder de vista el control de pérdidas.",
            "Se podría decir que vas a tomar de benchmark un rendimiento de mercado."
        ],
    },
    "avanzado": {
        "profile": "Agresivo",
        "front_level": "Avanzado",
        "description": [
            "Buscás generar rendimientos sensiblemente superiores al benchmark promedio de mercado.",
            "Para esto tomás mayores riesgos que se pueden traducir en importantes pérdidas de capital, pero sos consciente de eso."
        ],
    },
}


class EvaluacionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        respuestas = request.data.get("respuestas", None)

        if not respuestas or not isinstance(respuestas, list):
            return JsonResponse({"error": "Invalid or missing 'respuestas'. It must be a non-empty list."}, status=400)
        
        last_answer = respuestas[-1]

        if last_answer in [1, 2]:
            level = "básico"
        elif last_answer == 3:
            level = "intermedio"
        elif last_answer in [4]:
            level = "avanzado"
        else:
            return JsonResponse({"error": f"Invalid value in 'respuestas'. Must be between 1 and 4."}, status=400)

        # Update experience level of the user
        user = request.user
        user.experience_level = level
        user.save()

        level_info = LEVEL_MAPPING[level]

        response_data = {
            "perfil": level_info["profile"],
            "nivel": level_info["front_level"],
            "descripción": level_info["description"],
        }

        return JsonResponse(response_data, json_dumps_params={"ensure_ascii": False})



# perfil y nivel y descripcion 

# from rest_framework.views import APIView
# from rest_framework.response import Response
# from .services import calcular_puntaje_y_nivel, crear_evaluacion, obtener_evaluaciones
# from .serializers import EvaluationsSerializer

# class EvaluacionView(APIView):

#     def get(self, request):
#         # Obtener el parámetro 'trader_name' de la solicitud (si se pasa)
#         trader_name = request.query_params.get('trader_name', None)
        
#         # Usar el servicio para obtener las evaluaciones
#         evaluaciones = obtener_evaluaciones(trader_name)
        
#         # Serializar los resultados
#         serializer = EvaluationsSerializer(evaluaciones, many=True)
        
#         return Response(serializer.data)

# from rest_framework.response import Response
# from rest_framework.views import APIView
# from django.contrib.sessions.models import Session
# from .services import calcular_puntaje_y_nivel, crear_evaluacion
# from rest_framework.permissions import AllowAny

# class EvaluacionView(APIView):
    
#     def post(self, request):

#         #se espera un json con el puntaje y con el campo "ultima_ventana: True o False"

#         # las respuestas del usuario de la solicitud
#         respuestas_usuario = request.data.get("respuestas")
#         ultima_ventana = request.data.get("ultima_ventana", False)
        
#         # el nombre del trader
#         trader_name = request.user.username  

#         # si es la primera ventana, inicializamos la sesión si es necesario
#         if "respuestas" not in request.session:
#             request.session["respuestas"] = []

#         # acumulamos las respuestas del usuario en la sesión
#         request.session["respuestas"].extend(respuestas_usuario)
#         request.session.modified = True 

#         # si es la última ventana, calculamos el puntaje
#         if ultima_ventana:
            
#             # calcular el puntaje y el nivel de riesgo
#             puntaje, nivel_riesgo = calcular_puntaje_y_nivel(request.session["respuestas"])

#             evaluacion = crear_evaluacion(
#                 user=request.user,
#                 trader_name=trader_name,
#                 puntaje=puntaje,
#                 nivel_riesgo=nivel_riesgo,
#                 total_preguntas=len(request.session["respuestas"])
#             )
            
#             del request.session["respuestas"]

#             return Response({
#                 "nivel_riesgo": evaluacion.risk_level,
#                 "puntaje": evaluacion.details,
#                 "trader_name": evaluacion.trader_name
#             })

#         # Si no es la última ventana, simplemente devolvemos un mensaje de éxito
#         return Response({"message": "Respuestas recibidas correctamente."})
