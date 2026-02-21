from pathlib import Path

import pytest

from resume_matcher.pipeline import rank_resumes_in_folder


def test_rank_resumes_in_folder_missing_path() -> None:
    with pytest.raises(FileNotFoundError):
        rank_resumes_in_folder(jd_text="python sql", folder_path=Path("missing-folder"))
