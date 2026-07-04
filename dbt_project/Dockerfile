FROM python:3.11-slim
RUN pip install --no-cache-dir dbt-postgres==1.8.0
WORKDIR /usr/app/dbt_project
ENV DBT_PROFILES_DIR=/usr/app/dbt_project
ENTRYPOINT ["dbt"]
CMD ["run"]
