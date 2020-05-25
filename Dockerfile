#FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7
FROM python:3.6
WORKDIR /code

#RUN apk add --no-cache gcc musl-dev linux-headers

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

EXPOSE 8000

COPY . .
CMD "chmod a+x ./startup_app.sh"

#ENTRYPOINT "uvicorn main:app --port 5000"
#RUN "python --version"

#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

CMD ["./startup_app.sh"]
