from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model

user = get_user_model()

VALID_CHOICES = {1, 2, 3, 4}

# EXPECTED_RESPONSES_COUNT 

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
            return JsonResponse({"error": "Invalid or missing 'respuestas'. It must be a non-empty list."}, status=400)
        
        if len(respuestas) != len(VALID_CHOICES):
            return JsonResponse(
                {
                    "error": f"Expected {len(VALID_CHOICES)} answers, but received {len(respuestas)}.",
                    "message": f"Please provide exactly {len(VALID_CHOICES)} answers."
                },
                status=400
            )
        
        invalid_responses = [resp for resp in respuestas if resp not in VALID_CHOICES]

        if invalid_responses:
            return JsonResponse({
                "error": "Invalid responses found.",
                "invalid_responses": invalid_responses,
                "message": "Must be between 1 and 4"
            }, status=400)

        max_score_per_question = max(VALID_CHOICES)
        percentage_scores = [(resp / max_score_per_question) * 100 for resp in respuestas]
        average_score = sum(percentage_scores) / len(VALID_CHOICES)

        level = None
        for level_key, level_data in LEVEL_MAPPING.items():
            min_score, max_score = level_data["score_range"]
            if min_score <= average_score <= max_score:
                level = level_key
                break

        if not level:
            return JsonResponse({"error": "Score out of valid range."}, status=400)


        # Update experience level of the user
        user = request.user
        user.experience_level = level
        user.save()

        level_info = LEVEL_MAPPING[level]

        response_data = {
            "perfil": level_info["profile"],
            "nivel": level_info["front_level"],
            "descripción": level_info["description"],
            "puntaje": round(average_score, 2),
            "rango_puntaje": f"{level_info['score_range'][0]}-{level_info['score_range'][1]}"
        }

        return JsonResponse(response_data, json_dumps_params={"ensure_ascii": False})


