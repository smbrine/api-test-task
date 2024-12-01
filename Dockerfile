FROM --platform=$BUILDPLATFORM python:3.11-bookworm

WORKDIR /app

COPY pyproject.toml poetry.lock ./

# Environment variables
ENV PYTHONPATH=./
ENV PYTHONUNBUFFERED=True


ARG DOCKER_TAG
ARG IMAGE
ARG REPO
ARG BUILDPLATFORM
ENV APP_VERSION=$DOCKER_TAG
ENV IMAGE=$IMAGE
ENV BUILDPLATFORM=$BUILDPLATFORM

RUN echo "Building Docker image $IMAGE:$APP_VERSION for $BUILDPLATFORM"

RUN apt-get update && apt-get install -y --no-install-recommends

RUN rm -rf /var/lib/apt/lists/*

RUN python -m ensurepip --upgrade && pip install --upgrade pip

RUN pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

COPY . .

CMD ["python", "-m", "app.main"]