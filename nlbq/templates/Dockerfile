FROM python:3.11-slim-buster

EXPOSE 8080
RUN pip install nlbq
WORKDIR /app
COPY ./ /app

CMD ["nlbq"]
