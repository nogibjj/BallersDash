
# https://hub.docker.com/_/python
FROM python:3.9-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Install production dependencies.
RUN pip install Flask gunicorn

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . .

# Install production dependencies.
RUN pip install  --no-cache-dir -r requirements.txt

ENV PORT 8080

CMD streamlit run --server.port 8080 --server.enableCORS false mylib/NbaStatsDash.py

#CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app