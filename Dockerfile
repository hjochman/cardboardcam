FROM python:3.7-buster

ARG USE_UID=1000
ARG USE_GID=1000

RUN apt-get update -y && \
    apt-get install -y libexempi8 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ADD ./requirements.txt /tmp/requirements.txt

RUN pip install -r /tmp/requirements.txt && \
    pip install uwsgi==2.0.19.1 && \
    rm -f /tmp/requirements.txt

ADD . /app
RUN chown -R ${USE_UID}:${USE_GID} /app

USER ${USE_UID}

WORKDIR /app

# CMD "ENV=prod python3 wsgi.py"
CMD ["/usr/local/bin/uwsgi", \
    "--http-socket", ":8000", \
    "--logto", "/app/logs/cardboardcam_uwsgi.log", \
    "--wsgi-file", "/app/wsgi.py", \
    "--callable", "app", "--max-requests", "1000", \
    "--master", "--processes", "1", "--chmod"]

#     "--uid", "${USE_UID}", "--gid", "${USE_GID}", \