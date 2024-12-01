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


