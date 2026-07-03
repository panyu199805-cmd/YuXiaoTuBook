from fastapi import APIRouter

from app.api.v1 import admin, auth, books, daily, favorites, home, user

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth")
api_router.include_router(user.router, prefix="/user")
api_router.include_router(home.router, prefix="/home")
api_router.include_router(home.site_router)
api_router.include_router(books.router, prefix="/books")
api_router.include_router(daily.router, prefix="/daily")
api_router.include_router(favorites.router, prefix="/favorites")
api_router.include_router(favorites.history_router, prefix="/history")
api_router.include_router(admin.router, prefix="/admin")
