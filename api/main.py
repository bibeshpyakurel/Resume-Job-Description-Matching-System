from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Annotated

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from resume_matcher.pipeline import rank_resumes_in_folder

app = FastAPI(title="Resume Matcher API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/match")
async def match_resumes(
    jd: Annotated[str, Form(...)],
    files: Annotated[list[UploadFile], File(...)],
) -> dict[str, object]:
    if not jd.strip():
        raise HTTPException(status_code=400, detail="Job description must not be empty")

    if not files:
        raise HTTPException(status_code=400, detail="At least one PDF is required")

    with TemporaryDirectory() as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        saved_count = 0

        for index, upload in enumerate(files, start=1):
            filename = upload.filename or f"resume_{index}.pdf"
            if not filename.lower().endswith(".pdf"):
                continue

            destination = temp_dir / filename
            content = await upload.read()
            destination.write_bytes(content)
            saved_count += 1

        if saved_count == 0:
            raise HTTPException(status_code=400, detail="No valid PDF files were provided")

        results = rank_resumes_in_folder(jd_text=jd, folder_path=temp_dir)

    return {
        "count": len(results),
        "results": [asdict(result) for result in results],
    }
