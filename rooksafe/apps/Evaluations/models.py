from django.db import models

#Tabla: evaluations
#id: INT (Primary Key)
#user_id: INT (Foreign Key to users)
#trader_name: VARCHAR
#risk_level: ENUM('bajo', 'medio', 'alto')
#details: TEXT
#created_at: TIMESTAMP

# from django.db import models

# from apps.users.models import User


# class Evaluations(models.Model):
#     id = models.AutoField(primary_key=True)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     trader_name = models.CharField(max_length=255)  
#     risk_level = models.CharField(max_length=12, choices=[('principiante', 'Principiante'),('intermedio', 'Intermedio'),('avanzado','Avanzado')])
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.user} - {self.risk_level} - {self.trader_name} - {self.created_at} "