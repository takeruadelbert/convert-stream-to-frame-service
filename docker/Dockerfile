FROM tiangolo/uvicorn-gunicorn-starlette:python3.8

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

ENV REPO_HOME=/home/stream-to-frame-service
RUN mkdir -p ${REPO_HOME}
COPY . ${REPO_HOME}
WORKDIR ${REPO_HOME}

RUN poetry install --no-dev