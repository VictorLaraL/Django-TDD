FROM python:3.9-alpine3.13

# Best practice for declare who is the maintainer
LABEL maintainer="victorlara.com"

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /temp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./app /app
WORKDIR /app
EXPOSE 8000

ARG DEV=false
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r /temp/requirements.txt && \
    if [ $DEV = "true" ]; \
        then /py//bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    rm -rf /tmp && \
    adduser \
        --disabled-password\
        --no-create-home \
        django-user

ENV PATH="/py/bin:$PATH"

USER django-user 