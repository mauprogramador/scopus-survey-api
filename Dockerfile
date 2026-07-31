FROM python:3.12.12-slim-trixie

LABEL org.opencontainers.image.created="2025-12-03T00:00:00Z"
LABEL org.opencontainers.image.title="ScopusSurveyAPI"
LABEL org.opencontainers.image.description="Web API for bibliographic survey of Scopus articles"
LABEL org.opencontainers.image.authors="mauprogramador <sir.silvabmauricio@gmail.com>"
LABEL org.opencontainers.image.version="3.2.6"
LABEL org.opencontainers.image.url="https://github.com/mauprogramador/scopus-survey-api"
LABEL org.opencontainers.image.documentation="https://mauprogramador.github.io/scopus-survey-api/"
LABEL org.opencontainers.image.source="https://github.com/mauprogramador/scopus-survey-api"
LABEL org.opencontainers.image.vendor="Instituto Federal de Educação, Ciência e Tecnologia do Mato Grosso do Sul (IFMS) - Campus Três Lagoas"
LABEL org.opencontainers.image.license="MIT"
LABEL org.opencontainers.image.base.digest="sha256:b43ff04d5df04ad5cabb80890b7ef74e8410e3395b19af970dcd52d7a4bff921"
LABEL org.opencontainers.image.base.name="python:3.12.12-slim-trixie"

ENV PYTHONUNBUFFERED=1
ENV DEBUG=0
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN pip install --upgrade pip setuptools wheel

COPY ./requirements.txt .

RUN pip install --no-cache-dir --no-deps -r requirements.txt

COPY ./src ./src
COPY ./web ./web

CMD ["python3", "-m", "src"]
