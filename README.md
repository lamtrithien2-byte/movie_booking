# Movie Booking System

## Run

```powershell
python -m alembic upgrade head
python -m uvicorn app.main:app --reload
```

Open API docs:

```text
http://localhost:8000/docs
```

## Structure

```text
app/
  api/             # HTTP endpoints
  db/              # PostgreSQL connection
  models/          # SQLAlchemy models
  repositories/    # DB query functions
  services/        # Business logic
  main.py
alembic/
  versions/        # Migration files
```

## APIs

Auth:

| Method | Endpoint | Note |
| --- | --- | --- |
| POST | `/auth/register` | Register user and return access token |
| POST | `/auth/login` | Login and return access token |
| GET | `/auth/me` | Decode token and return current user |

User:

| Method | Endpoint | Note |
| --- | --- | --- |
| GET | `/movies?page=1&size=10` | List active movies |
| GET | `/movies?keyword=aven&type=Action` | Search movie by title and type |
| GET | `/movies/{movie_id}` | Movie detail |
| GET | `/cinemas?page=1&size=10` | List active cinemas |
| GET | `/cinemas?city=Ho Chi Minh` | Filter cinema by city |
| GET | `/cinemas/{cinema_id}` | Cinema detail |

Admin:

| Method | Endpoint | Note |
| --- | --- | --- |
| GET | `/admin/users` | List users |
| GET | `/admin/roles` | List roles |
| GET | `/admin/movies` | List all movies |
| POST | `/admin/movies` | Create movie |
| PUT | `/admin/movies/{movie_id}` | Update movie |
| DELETE | `/admin/movies/{movie_id}` | Delete movie |
| GET | `/admin/cinemas` | List all cinemas |
| POST | `/admin/cinemas` | Create cinema |
| PUT | `/admin/cinemas/{cinema_id}` | Update cinema |
| DELETE | `/admin/cinemas/{cinema_id}` | Delete cinema |

## Auth

Send token in Postman:

```text
Authorization -> Bearer Token -> paste access_token
```

Admin APIs require token with role `admin`.
