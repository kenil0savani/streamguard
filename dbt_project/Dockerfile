FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir "dbt-core>=1.8,<1.9" "dbt-postgres>=1.8,<1.9"
WORKDIR /usr/app/dbt_project
ENV DBT_PROFILES_DIR=/usr/app/dbt_project
ENTRYPOINT ["dbt"]
CMD ["run"]
