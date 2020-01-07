FROM postgres:12

ENV POSTGRES_DB i2b2
ENV POSTGRES_USER i2b2
ENV POSTGRES_PASSWORD i2b2

RUN mkdir -p /var/lib/postgresql-static/data
ENV PGDATA /var/lib/postgresql-static/data

COPY sql/* /docker-entrypoint-initdb.d/

EXPOSE 5432