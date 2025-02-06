FROM python:3.10-alpine
COPY . /app
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

ENV FLASK_EVN production

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "marino:create_app()"]