from fastapi import FastAPI;
from Routes import FlashCardGenerator, QuizGenerator, LectureTranscriber, NotesSummarizer, SignIn, SignUp, Home

app = FastAPI()

app.include_router(Home.router, prefix="/Home", tags=["Home"])
app.include_router(SignUp.router, prefix="SignUp", tags=["SignUp"])
app.include_router(SignIn.router, prefix="SignIn", tags=["SignIn"])
app.include_router(QuizGenerator.router, prefix="/QuizGenerator", tags=["QuizGenerator"])
app.include_router(FlashCardGenerator.router, prefix="/FlashCardGenerator", tags=["FlashCardGenerator"])
app.include_router(LectureTranscriber.router, prefix="/LectureTranscriber", tags=["LectureTranscriber"])
app.include_router(NotesSummarizer.router, prefix="/NotesSummarizer", tags=["NotesSummarizer"])
