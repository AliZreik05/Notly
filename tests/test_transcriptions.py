import io
import os

from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_upload_and_history_and_detail(tmp_path):
    # Prepare a small fake audio file-like object
    audio_bytes = b"RIFF....WAVEfmt "  # not a real audio but accepted by upload handler
    files = {"file": ("test.wav", io.BytesIO(audio_bytes), "audio/wav")}

    # Upload
    resp = client.post(
        "/api/v1/transcriptions/upload?user_id=1",
        files=files,
        data={"title": "Test Lecture", "course_name": "TEST101"},
    )
    assert resp.status_code in (200, 201)
    body = resp.json()
    assert "id" in body
    assert "status" in body

    transcription_id = body["id"]

    # History should include the new transcription
    resp2 = client.get("/api/v1/transcriptions/history?user_id=1")
    assert resp2.status_code == 200
    hist = resp2.json()
    assert any(item["id"] == transcription_id for item in hist)

    # Detail should return the transcription content
    resp3 = client.get(f"/api/v1/transcriptions/{transcription_id}?user_id=1")
    assert resp3.status_code == 200
    detail = resp3.json()
    assert detail["id"] == transcription_id
    # transcript_text should exist (stubbed if no API key)
    assert "transcript_text" in detail
