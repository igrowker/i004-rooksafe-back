# Use an official Python image as the base image
FROM python:3.12-bookworm


# Set the working directory
WORKDIR /usr/share/app

# Copy the requirements.txt file to the working directory
COPY rooksafe/requirements.txt .

# Install the required packages
RUN pip install -r requirements.txt

# Copy the rest of the application files
COPY rooksafe/  .


# Collect static files
#RUN python manage.py collectstatic --no-input
RUN find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
RUN find . -path "*/migrations/*.pyc"  -delete



#For production
CMD ["uwsgi","--ini", "uwsgi.ini"]
