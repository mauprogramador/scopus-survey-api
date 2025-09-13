FROM python:3.12.11-slim-trixie

ENV WORKDIR=/usr/scopus-survey-api
WORKDIR $WORKDIR

RUN pip install --upgrade pip && pip3 install wheel && pip3 install poetry

COPY ./pyproject.toml $WORKDIR
COPY ./poetry.lock $WORKDIR

RUN poetry install --with test

COPY ./src $WORKDIR/src
COPY ./tests $WORKDIR/tests
COPY ./web $WORKDIR/web

CMD ["poetry", "run", "python3", "-m", "src"]
