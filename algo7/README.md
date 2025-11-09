# synder-algo7

- Adrian Goral
- Bartłomiej Kuk
- Mateusz Andrzejewski
- Adam Krzywicki

## Struktura repo

```
synder-algo7/
├── frontend/        # React + Vite + TypeScript
└── backend/         # Spring Boot 3 (Java 21, Maven)
```

## Wymagania
- Docker Desktop (do uruchomienia Postgres):
- - `docker run --name synder-algo7-db -e POSTGRES_USER=synder -e POSTGRES_PASSWORD=synder_password -e POSTGRES_DB=synder_algo7 -p 5432:5432 -v postgres_data:/var/lib/postgresql/data -d postgres:16-alpine`
- Node.js 22 LTS + npm
- - `npm i`
- - `npm run dev`
- Java 21 + Maven
- - `mvn spring-boot:run`