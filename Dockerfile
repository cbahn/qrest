FROM python:3.10-alpine
COPY . /app
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

RUN export FLASK_EVN=development

# "--chdir hello" is needed to specify which directory app.py can be found
  # Note, I tried running it with "hello.app:app" but it lead to problems finding packages.
  # I've been developing while in the hello/ directory this whole time, so i'm going to run 
  # gunicorn from there to ensure consistency.

# "-w 3" specifies that three processes should be handling requests. Is that the right number ¯\_(ツ)_/¯
# If the app file were named myapp.py then the final line of the command would be "myapp:app"

CMD ["gunicorn", "--chdir", "hello", "-w", "3", "-b", "0.0.0.0:8080", "app:app"]

# CMD ["tail", "-f", "/dev/null"]