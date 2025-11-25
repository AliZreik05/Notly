import os
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile


@dataclass
class StoredFile:
    absolute_path: Path
    public_url: str


def _get_media_root() -> Path:
    root = Path(os.getenv("MEDIA_ROOT", "media"))
    root.mkdir(parents=True, exist_ok=True)
    return root


def _get_transcription_dir() -> Path:
    directory = _get_media_root() / "transcriptions"
    directory.mkdir(parents=True, exist_ok=True)
    return directory


async def store_audio_file(upload: UploadFile, user_id: int) -> StoredFile:
    """
    Persist an uploaded audio file locally so it can be processed later.
    """
    extension = Path(upload.filename or "").suffix.lower() or ".wav"
    random_segment = uuid4().hex[:8]
    destination = _get_transcription_dir() / f"user-{user_id}-{random_segment}{extension}"

    with destination.open("wb") as out_file:
        contents = await upload.read()
        out_file.write(contents)

    public_url = f"/media/transcriptions/{destination.name}"
    return StoredFile(absolute_path=destination, public_url=public_url)

