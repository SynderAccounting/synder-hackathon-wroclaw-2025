#!/usr/bin/env bash
docker exec -i synderhacks-postgres psql -U synderhacks -d synderhacks -c "CREATE DATABASE multitenant_db"
docker exec -i synderhacks-postgres psql -U synderhacks -d multitenant_db < init-scripts-schema/01*
docker exec -i synderhacks-postgres psql -U synderhacks -d multitenant_db < init-scripts-schema/02*
docker exec -i synderhacks-postgres psql -U synderhacks -d multitenant_db < init-scripts-schema/03*
docker exec -i synderhacks-postgres psql -U synderhacks -d multitenant_db < init-scripts-schema/04*
