from fastapi import FastAPI;

app = FastAPI()

@app.get("/home")
def root():
    return {"hello" : "world"}

@app.get("/signup")
def signup():
    return 

@app.get("/signin")
def signin():
    return

app.get("/quizGenerator")
def quizGenerator():
    return

app.get("/flashCardGenerator")
def flashCardGenerator():
    return

app.get("/lectureTranscriber")
def lectureTranscriber():
    return

app.get("/notesOrganizer")
def notesOrganizer():
    return