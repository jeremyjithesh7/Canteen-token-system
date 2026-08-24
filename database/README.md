# Database Setup & Migration Guide

## Overview
The Digital Canteen Token System uses a normalized **PostgreSQL** database schema with 17 relational tables, strict foreign key constraints, check constraints, default timestamps, and high-performance b-tree indexes.

## Files
- [`schema.sql`](file:///Users/jeremyjithesh/mini%20project/database/schema.sql): Complete DDL table creation script.
- [`seed.sql`](file:///Users/jeremyjithesh/mini%20project/database/seed.sql): Production-grade realistic sample data including users, categories, 20 food items, daily menu, initial inventory, preferences, sample orders, tokens, payments, and AI predictions.

## PostgreSQL Manual Setup
1. Ensure PostgreSQL is installed and running:
   ```bash
   psql -U postgres
   ```
2. Create the database:
   ```sql
   CREATE DATABASE canteen_db;
   CREATE USER canteen_user WITH ENCRYPTED PASSWORD 'canteen_password';
   GRANT ALL PRIVILEGES ON DATABASE canteen_db TO canteen_user;
   ```
3. Run the schema and seed scripts:
   ```bash
   psql -U canteen_user -d canteen_db -f database/schema.sql
   psql -U canteen_user -d canteen_db -f database/seed.sql
   ```

## Docker Compose Quickstart
Start PostgreSQL and Adminer with 1 command:
```bash
docker-compose up -d postgres adminer
```
- PostgreSQL Port: `5432`
- Adminer Database UI: `http://localhost:8080` (System: PostgreSQL, Server: postgres, User: postgres, Password: postgrespassword, DB: canteen_db)

## Automatic Fallback
When running the FastAPI backend locally without a live PostgreSQL instance, SQLAlchemy automatically initializes an embedded SQLite database (`canteen.db`) and seeds it with default data on startup. To target PostgreSQL, set `DATABASE_URL` in `backend/.env`.
