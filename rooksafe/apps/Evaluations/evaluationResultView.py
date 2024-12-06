from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model

user = get_user_model()

VALID_CHOICES = [1, 2, 3, 4]
TOTAL_SCORE = 100
QUESTION_WEIGHT = TOTAL_SCORE / len(VALID_CHOICES)


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
        "score_range": (0, 45),
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
        "score_range": (46, 80),
    },
    "avanzado": {
        "profile": "Agresivo",
        "front_level": "Avanzado",
        "description": [
            "Buscás generar rendimientos sensiblemente superiores al benchmark promedio de mercado.",
            "Para esto tomás mayores riesgos que se pueden traducir en importantes pérdidas de capital, pero sos consciente de eso."
        ],
        "score_range": (80, 100),
    },
}


class EvaluacionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        respuestas = request.data.get("respuestas", None)

        if not respuestas or not isinstance(respuestas, list):
            return JsonResponse({"error": "Respuestas inválidas o faltantes. Debe ser una lista no vacía."}, status=400)
        
        if len(respuestas) != len(VALID_CHOICES):
            return JsonResponse(
                {
                    "error": f"Se esperaban {len(VALID_CHOICES)} respuestas, pero se recibieron {len(respuestas)}.",
                    "message": f"Por favor, proporciona exactamente {len(VALID_CHOICES)} respuestas."
                },
                status=400
            )
        # Validate that each answer is within the allowed range
        for answer in respuestas:
            if not (1 <= answer <= 4):
                return JsonResponse(
                    {
                        "error": "Fuera del rango permitido.",
                        "message": "Cada respuesta debe estar entre 1 y 4."
                    },
                    status=400
                )
        ###
        total_score = 0
        for i, answer in enumerate(respuestas):
            if i < len(VALID_CHOICES) and answer == VALID_CHOICES[i]:
                total_score += QUESTION_WEIGHT  # add question_weight for each good answer

        level = None
        for level_key, level_data in LEVEL_MAPPING.items():
            min_score, max_score = level_data["score_range"]
            if min_score <= total_score <= max_score:
                level = level_key
                break

        if not level:
            return JsonResponse({"error":"Fuera del rango de puntuación."})

        # Update experience level of the user
        user = request.user
        user.experience_level = level
        user.save()

        level_info = LEVEL_MAPPING[level]

        response_data = {
            "perfil": level_info["profile"],
            "nivel": level_info["front_level"],
            "descripcion": level_info["description"],
            "puntaje": round(total_score, 2),
            "rango_puntaje": f"{level_info['score_range'][0]}-{level_info['score_range'][1]}"
        }

        #return JsonResponse(response_data, json_dumps_params={"ensure_ascii": False})
        return JsonResponse(response_data)

