from django.db import models


class PriceData(models.Model):
    symbol = models.CharField(max_length=10)  # Símbolo del mercado, e.g., "AAPL"
    timestamp = models.DateTimeField()       # Tiempo del precio
    open_price = models.FloatField()         # Precio de apertura
    high_price = models.FloatField()         # Precio más alto
    low_price = models.FloatField()          # Precio más bajo
    close_price = models.FloatField()        # Precio de cierre
    volume = models.FloatField()             # Volumen de trading

    class Meta:
        unique_together = ('symbol', 'timestamp')  # Evitar duplicados

    def __str__(self):
        return f"{self.symbol} - {self.timestamp}"