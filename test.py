from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
        <head>
            <title>Trang chủ</title>
        </head>
        <body>
            <h1>Trang chủ</h1>

            <button onclick="window.location.href='/movies'">
                Xem danh sách phim
            </button>

        </body>
    </html>
    """

@app.get("/get")

@app.get("/movies")
def get_movies():
    return ["Avengers", "Batman", "Spider-Man"]