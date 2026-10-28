FROM python:3.11-slim
ENV DB_PASSWORD=Yerba2025!
WORKDIR /app
ADD requirements.txt /app/
RUN pip install -r requirements.txt
ADD . /app
EXPOSE 80
CMD gunicorn -b 0.0.0.0:80 app:app
