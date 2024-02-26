FROM python:3.11.1-buster

ENV WORKDIR=/usr/src/scopussearcherapi
WORKDIR $WORKDIR

RUN python3 -m pip install --upgrade pip

COPY ./requirements/requirements.txt $WORKDIR
RUN pip3 install --no-cache-dir -r requirements.txt

COPY ./requirements/requirements-test.txt $WORKDIR
RUN pip3 install --no-cache-dir -r requirements-test.txt

COPY ./app $WORKDIR/app
COPY ./tests $WORKDIR/tests
COPY ./Makefile $WORKDIR

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0"]
