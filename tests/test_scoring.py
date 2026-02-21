from resume_matcher.scoring import compute_scores, cosine_score, final_score, overlap_score


def test_overlap_score():
    jd = {"python", "sql", "aws"}
    resume = {"python", "sql", "docker"}
    assert overlap_score(jd, resume) == 66.67


def test_cosine_score_binary_vectors():
    jd = {"python", "sql", "aws"}
    resume = {"python", "sql", "docker"}
    assert cosine_score(jd, resume) == 66.67


def test_final_score_weighted_average():
    assert final_score(80.0, 60.0) == 70.0


def test_compute_scores_returns_all_values():
    jd = {"python", "sql"}
    resume = {"python"}
    overlap, cosine, final = compute_scores(jd, resume)
    assert overlap == 50.0
    assert cosine == 70.71
    assert final == 60.35
