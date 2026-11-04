FROM python:3.13-slim-bookworm@sha256:281d39ff02e3b389401586134ff9e6572954687822a58055ec07a60ded4e0b7f

WORKDIR /app
COPY --chown=1000:2000 app.py /app/app.py
USER 1000:2000

ENTRYPOINT ["python", "-u", "/app/app.py"]
