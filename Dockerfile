FROM python:3.10-alpine
COPY . /app
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

ENV FLASK_EVN production

# I'm running this on a 32 logical core cpu so I'm going to run with 33 workers
CMD ["gunicorn", "-w", "33", "-b", "0.0.0.0:8080", "marino:create_app()"]