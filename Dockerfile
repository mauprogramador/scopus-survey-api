FROM python:3.11.1-buster

ENV WORKDIR=/usr/src/scopussearcherapi
WORKDIR $WORKDIR

RUN pip install --upgrade pip && pip3 install wheel && pip3 install poetry

COPY ./pyproject.toml $WORKDIR
COPY ./poetry.lock $WORKDIR

RUN poetry install --with test

COPY ./app $WORKDIR/app
COPY ./tests $WORKDIR/tests
COPY ./web $WORKDIR/web

CMD ["poetry", "run", "python3", "-m", "app"]
