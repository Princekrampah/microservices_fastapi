Docker Postgres setup

```terminal
docker run --name postgres-db -e POSTGRES_PASSWORD=testdb123 -d -p 5442:5432 postgres
```