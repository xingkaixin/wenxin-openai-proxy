FROM tiangolo/uvicorn-gunicorn:python3.8
WORKDIR /app
ENV PYTHONPATH=/app
COPY ./app ./app
COPY *.py ./
COPY *.toml ./
COPY README.md ./
COPY ./requirements.lock  ./requirements.txt
RUN pip install  -r requirements.txt


EXPOSE 6000