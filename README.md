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

Open simple flow test page:

```text
http://localhost:8000/flow-test
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
| GET | `/cinemas?city=Ho Chi Minh&district=Quan 1` | Filter cinema by city and district |
| GET | `/cinemas/{cinema_id}` | Cinema detail |
| GET | `/rooms?cinema_id=4` | List rooms in one cinema |
| GET | `/rooms?showtime_id=5` | Get room of one showtime |
| GET | `/rooms/{room_id}` | Room detail |
| GET | `/showtimes?page=1&size=10` | List active showtimes |
| GET | `/showtimes?movie_title=batman&date=2026-04-22` | Search showtimes by movie title |
| GET | `/showtimes?movie_title=batman&cinema_id=4` | Search showtimes by selected cinema |
| GET | `/showtimes?movie_title=batman&city=Ho Chi Minh&district=Quan 7&date=2026-04-22` | Search showtimes like a user, response includes room name |
| GET | `/showtimes/{showtime_id}` | Showtime detail |
| GET | `/showtimes/{showtime_id}/seat-map` | Seat map with available and booked seats |
| POST | `/showtimes/{showtime_id}/seat-map/preview` | Preview selected seats and check single empty seat rule |
| POST | `/showtimes/{showtime_id}/seats/book` | Book selected seats |

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
| GET | `/admin/rooms` | List all rooms |
| POST | `/admin/rooms` | Create room |
| PUT | `/admin/rooms/{room_id}` | Update room |
| DELETE | `/admin/rooms/{room_id}` | Delete room |
| GET | `/admin/showtimes` | List all showtimes |
| POST | `/admin/showtimes` | Create showtime with `room_id`, `show_date`, and `show_time` |
| PUT | `/admin/showtimes/{showtime_id}` | Update showtime with `room_id`, `show_date`, and `show_time` |
| DELETE | `/admin/showtimes/{showtime_id}` | Delete showtime |

## Auth

Send token in Postman:

```text
Authorization -> Bearer Token -> paste access_token
```

Public APIs like `/movies`, `/cinemas`, `/showtimes`, `/rooms` do not need token.
Admin APIs require token with role `admin`.

## PgAdmin helper

Use this view when you want showtimes with movie and cinema names:

```sql
SELECT * FROM showtime_details;
```

Showtimes now also include `room_id` and `room_name`.
