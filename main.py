from fastapi import FastAPI
from contextlib import asynccontextmanager
from db.sessions import engine, Base

from Routes.Home import router as home_router
from Routes.SignUp import router as signup_router
from Routes.SignOut import router as signout_router
from Routes.SignIn import router as signin_router
from Routes.QuizGenerator import router as quiz_router
from Routes.FlashCardGenerator import router as flash_router
from Routes.LectureTranscriber import router as lecture_router
from Routes.NotesSummarizer import router as notes_router
from Routes.Lecture import router as lecture_router
from Routes.History import router as history_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")
    yield
    print("Application is shutting down")

app = FastAPI(lifespan=lifespan)

app.include_router(home_router)
app.include_router(signup_router)
app.include_router(signout_router)
app.include_router(signin_router)
app.include_router(quiz_router)
app.include_router(flash_router)
app.include_router(lecture_router)
app.include_router(notes_router)
app.include_router(lecture_router)
app.include_router(history_router)
