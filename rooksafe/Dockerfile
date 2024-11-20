# Imagen base de Python
FROM python:3

# Establecer el directorio de trabajo en la raíz del proyecto
WORKDIR /rooksafe

# Copiar todos los archivos del proyecto al contenedor
COPY . /rooksafe

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto del servidor Django
EXPOSE 3000

# Comando predeterminado para ejecutar Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:3000"]
