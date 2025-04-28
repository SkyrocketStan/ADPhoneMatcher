FROM python:3.7-slim

# Установка pytest и pylint
RUN pip install --no-cache-dir pytest==7.4.4 pylint==2.17.7

WORKDIR /app