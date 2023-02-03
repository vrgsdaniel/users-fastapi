# Build
FROM python:3.10-slim-buster AS build
RUN apt-get update \
    && apt-get install gcc -y \
    && apt-get clean
COPY requirements.txt /app/
WORKDIR /app
RUN python -m venv --copies ./venv
ENV PATH ./venv/bin:$PATH
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
COPY src /app/src
COPY pyproject.toml pyproject.toml
RUN pip install --no-cache-dir .

# Could include tests in a dirrefent image, we will run them in the CI though

# Final image
FROM python:3.10-slim-buster AS prod
WORKDIR /app
RUN adduser -u 1000 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser
COPY --from=build /app/venv /app/venv/
ENV PATH /app/venv/bin:$PATH
WORKDIR /app
EXPOSE 8080
CMD ["uvicorn", "users_fastapi.main:app", "--host", "0.0.0.0", "--port", "8080"]
