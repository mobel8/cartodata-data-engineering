# Image reproductible : pipeline + dbt + Dagster + API en une commande.
FROM python:3.11-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PYTHONUTF8=1 \
    PYTHONIOENCODING=utf-8 \
    DAGSTER_HOME=/app/dagster_home

# Dépendances d'abord (cache de couche Docker)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN pip install --no-cache-dir -e . && mkdir -p /app/dagster_home

EXPOSE 8000 3000

# Par défaut : rejoue le pipeline ELT (override via docker-compose).
CMD ["python", "-m", "cartodata_de.pipeline", "--ci", "--no-export"]
