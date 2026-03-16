from fastapi import FastAPI

from core.database.db_connection import engine
from routers import auth, lessons, admin

app = FastAPI()
print(engine.url)
app.include_router(auth.router)
app.include_router(lessons.router)
app.include_router(admin.router)
