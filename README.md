# Movie Booking System

## File dang dung
- `app/db/database.py`: ket noi PostgreSQL
- `app/models/user.py`: model `User` map voi bang `users`
- `app/main.py`: FastAPI app

## User APIs

| Method | Endpoint | Chuc nang | Request | Response | Status |
| --- | --- | --- | --- | --- | --- |
| POST | `/auth/register` | Dang ky tai khoan | Body: `full_name`, `email`, `phone`, `password` | `message`, `data:{id, full_name, email, phone}` | 200, 400, 500 |
| POST | `/auth/login` | Dang nhap | Body: `email`, `password` | `message`, `data:{access_token, user}` | 200, 401, 500 |
| POST | `/auth/logout` | Dang xuat | Khong co body | `message` | 200, 401, 500 |
| GET | `/users/me` | Lay thong tin user hien tai | Header token | `data:{id, full_name, email, phone, role}` | 200, 401, 404, 500 |
| PUT | `/users/me` | Cap nhat thong tin user | Header token, Body: `full_name`, `phone` | `message`, `data:{id, full_name, email, phone}` | 200, 400, 401, 500 |
| GET | `/movies` | Lay danh sach phim | Query: `page`, `keyword`, `status` | `data:[{id, title, duration}]` | 200, 400, 500 |
| GET | `/movies/{movie_id}` | Lay chi tiet phim | Path: `movie_id` | `data:{id, title, description, duration}` | 200, 404, 500 |
| GET | `/theaters` | Lay danh sach rap | Query: `city`, `keyword` | `data:[{id, name, city, address}]` | 200, 400, 500 |
| GET | `/showtimes` | Lay danh sach suat chieu | Query: `movie_id`, `theater_id`, `date` | `data:[{id, movie_id, theater_id, start_time, price}]` | 200, 400, 500 |
| GET | `/showtimes/{showtime_id}/seats` | Lay danh sach ghe | Path: `showtime_id` | `data:{showtime_id, seats:[{seat_code, status}]}` | 200, 404, 500 |
| POST | `/bookings` | Tao booking | Header token, Body: `showtime_id`, `seat_ids`, `payment_method` | `message`, `data:{booking_id, total_amount, status}` | 200, 400, 401, 500 |
| GET | `/bookings` | Lay danh sach booking cua user | Header token, Query: `page`, `status` | `data:[{id, movie_title, showtime, status}]` | 200, 401, 500 |
| GET | `/bookings/{booking_id}` | Lay chi tiet booking | Header token, Path: `booking_id` | `data:{id, movie_title, seats, total_amount, status}` | 200, 401, 404, 500 |
| POST | `/bookings/{booking_id}/pay` | Thanh toan booking | Header token, Path: `booking_id`, Body: `payment_method`, `transaction_id` | `message`, `data:{booking_id, payment_status}` | 200, 400, 401, 404, 500 |
| POST | `/bookings/{booking_id}/cancel` | Huy booking | Header token, Path: `booking_id` | `message`, `data:{booking_id, status}` | 200, 400, 401, 404, 500 |
| GET | `/tickets/{ticket_id}` | Lay ve dien tu | Header token, Path: `ticket_id` | `data:{ticket_id, booking_id, qr_code}` | 200, 401, 404, 500 |

## Admin APIs

| Method | Endpoint | Chuc nang | Request | Response | Status |
| --- | --- | --- | --- | --- | --- |
| GET | `/admin/dashboard` | Lay tong quan he thong | Header admin token | `data:{total_users, total_movies, total_bookings, today_revenue}` | 200, 401, 500 |
| GET | `/admin/users` | Lay danh sach user | Header admin token, Query: `page`, `keyword`, `status` | `data:[{id, full_name, email, status}]` | 200, 401, 500 |
| GET | `/admin/users/{user_id}` | Lay chi tiet user | Header admin token, Path: `user_id` | `data:{id, full_name, email, phone, status}` | 200, 401, 404, 500 |
| PUT | `/admin/users/{user_id}/status` | Khoa/mo user | Header admin token, Path: `user_id`, Body: `status` | `message`, `data:{id, status}` | 200, 400, 401, 404, 500 |
| GET | `/admin/movies` | Lay danh sach phim | Header admin token, Query: `page`, `keyword`, `status` | `data:[{id, title, duration, status}]` | 200, 401, 500 |
| POST | `/admin/movies` | Tao phim moi | Header admin token, Body: `title`, `description`, `duration`, `genre`, `release_date` | `message`, `data:{id, title}` | 200, 400, 401, 500 |
| PUT | `/admin/movies/{movie_id}` | Cap nhat phim | Header admin token, Path: `movie_id`, Body: phim can sua | `message`, `data:{id, title, status}` | 200, 400, 401, 404, 500 |
| DELETE | `/admin/movies/{movie_id}` | Xoa phim | Header admin token, Path: `movie_id` | `message` | 200, 401, 404, 500 |
| GET | `/admin/theaters` | Lay danh sach rap | Header admin token, Query: `page`, `keyword`, `city` | `data:[{id, name, city, address}]` | 200, 401, 500 |
| POST | `/admin/theaters` | Tao rap moi | Header admin token, Body: `name`, `city`, `address` | `message`, `data:{id, name}` | 200, 400, 401, 500 |
| PUT | `/admin/theaters/{theater_id}` | Cap nhat rap | Header admin token, Path: `theater_id`, Body: `name`, `city`, `address` | `message`, `data:{id, name}` | 200, 400, 401, 404, 500 |
| DELETE | `/admin/theaters/{theater_id}` | Xoa rap | Header admin token, Path: `theater_id` | `message` | 200, 401, 404, 500 |
| GET | `/admin/rooms` | Lay danh sach phong chieu | Header admin token, Query: `theater_id` | `data:[{id, theater_id, name, total_rows, total_cols}]` | 200, 401, 500 |
| POST | `/admin/rooms` | Tao phong chieu | Header admin token, Body: `theater_id`, `name`, `total_rows`, `total_cols` | `message`, `data:{id, name}` | 200, 400, 401, 500 |
| PUT | `/admin/rooms/{room_id}` | Cap nhat phong chieu | Header admin token, Path: `room_id`, Body: phong can sua | `message`, `data:{id, name}` | 200, 400, 401, 404, 500 |
| DELETE | `/admin/rooms/{room_id}` | Xoa phong chieu | Header admin token, Path: `room_id` | `message` | 200, 401, 404, 500 |
| GET | `/admin/showtimes` | Lay danh sach suat chieu | Header admin token, Query: `movie_id`, `theater_id`, `date` | `data:[{id, movie_id, room_id, start_time, price}]` | 200, 401, 500 |
| POST | `/admin/showtimes` | Tao suat chieu | Header admin token, Body: `movie_id`, `room_id`, `start_time`, `end_time`, `price` | `message`, `data:{id, movie_id, room_id}` | 200, 400, 401, 500 |
| PUT | `/admin/showtimes/{showtime_id}` | Cap nhat suat chieu | Header admin token, Path: `showtime_id`, Body: suat chieu can sua | `message`, `data:{id, price}` | 200, 400, 401, 404, 500 |
| DELETE | `/admin/showtimes/{showtime_id}` | Xoa suat chieu | Header admin token, Path: `showtime_id` | `message` | 200, 401, 404, 500 |
| GET | `/admin/bookings` | Lay danh sach booking | Header admin token, Query: `page`, `status`, `from_date`, `to_date` | `data:[{id, user_name, movie_title, status}]` | 200, 401, 500 |
| GET | `/admin/bookings/{booking_id}` | Lay chi tiet booking | Header admin token, Path: `booking_id` | `data:{id, user_name, movie_title, seats, total_amount, status}` | 200, 401, 404, 500 |
| PUT | `/admin/bookings/{booking_id}/status` | Cap nhat trang thai booking | Header admin token, Path: `booking_id`, Body: `status` | `message`, `data:{id, status}` | 200, 400, 401, 404, 500 |
| GET | `/admin/reports/revenue` | Bao cao doanh thu | Header admin token, Query: `from_date`, `to_date`, `group_by` | `data:{total_revenue, items}` | 200, 400, 401, 500 |
| GET | `/admin/reports/movies` | Bao cao phim ban chay | Header admin token, Query: `from_date`, `to_date`, `limit` | `data:[{movie_id, title, tickets_sold, revenue}]` | 200, 400, 401, 500 |

## API hien tai trong code
- `GET /`
- `GET /db-check`
- `POST /users`
