from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, Text, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Enum as SAEnum
import enum
from db.sessions import Base
from uuid import uuid4

class SourceType(str, enum.Enum):
    note = "note"
    transcript = "transcript"
    manual = "manual"

class ExamSource(str, enum.Enum):
    note = "note"
    transcript = "transcript"
    manual = "manual"

class TranscriptionStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    firstName = Column(String(255), nullable=False)
    lastName = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    notes = relationship("Note", back_populates="owner")
    quizes = relationship("Exam", back_populates="owner")           # keep name as-is
    flashcards = relationship("FlashCard", back_populates="owner")  # FIX: class name & back_populates
    transcriptions = relationship("Transcription", back_populates="owner")


class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(255), nullable=False)
    content = Column(String(2000), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="notes")


class FlashCardDeck(Base):
    __tablename__ = "flashcard_deck"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(255), nullable=False)
    source_type = Column(SAEnum(SourceType, name="source_type", native_enum=True), nullable=False)
    source_id = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    cards = relationship("FlashCard", back_populates="set", cascade="all, delete")  # FIX: class name


class FlashCard(Base):
    __tablename__ = "flashcard"
    id = Column(Integer, primary_key=True, index=True)
    set_id = Column(Integer, ForeignKey("flashcard_deck.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    prompt = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)

    set = relationship("FlashCardDeck", back_populates="cards")  # FIX: class name
    owner = relationship("User", back_populates="flashcards")    # FIX: counterpart for User.flashcards


class Exam(Base):
    __tablename__ = "exam"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    grade = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    title = Column(String(255), nullable=False)
    source_type = Column(SAEnum(ExamSource, name="exam_source", native_enum=True), nullable=False)
    source_id = Column(Integer, nullable=True)
    result_details = Column(JSON, nullable=True)

    questions = relationship("ExamQuestion", back_populates="exam", cascade="all, delete")
    owner = relationship("User", back_populates="quizes")  # FIX: counterpart for User.quizes


class ExamQuestion(Base):
    __tablename__ = "examQuestion"
    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exam.id"), index=True, nullable=False)
    question = Column(Text, nullable=False)
    options = Column(JSONB, nullable=False) 
    answer_idx = Column(Integer, nullable=False)
    points = Column(Integer, default=1)
    order = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    exam = relationship("Exam", back_populates="questions")


class Transcription(Base):
    __tablename__ = "transcriptions"
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    course_name = Column(String(255), nullable=True)
    audio_url = Column(String(512), nullable=False)
    audio_path = Column(String(1024), nullable=False)
    transcript_text = Column(Text, nullable=True)
    summary_text = Column(Text, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    word_count = Column(Integer, nullable=True)
    status = Column(
        SAEnum(TranscriptionStatus, name="transcription_status", native_enum=True),
        nullable=False,
        server_default=TranscriptionStatus.PENDING.value,
    )
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    owner = relationship("User", back_populates="transcriptions")
