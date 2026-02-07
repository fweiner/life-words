"""Integration tests for matching endpoints."""


def test_evaluate_name_answer(client):
    """Test the name evaluation endpoint."""
    response = client.post(
        "/api/matching/evaluate/name",
        json={
            "user_answer": "John",
            "expected_name": "John Smith",
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_correct"] is True
    assert data["matched_via"] == "first_name"


def test_evaluate_name_no_match(client):
    """Test name evaluation with no match."""
    response = client.post(
        "/api/matching/evaluate/name",
        json={
            "user_answer": "completely wrong",
            "expected_name": "John Smith",
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_correct"] is False


def test_evaluate_question_answer(client):
    """Test the question evaluation endpoint."""
    response = client.post(
        "/api/matching/evaluate/question",
        json={
            "user_answer": "pizza",
            "expected_answer": "pizza",
            "acceptable_answers": ["pie"],
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_correct"] is True
    assert data["score"] == 1.0


def test_evaluate_information_answer(client):
    """Test the information evaluation endpoint."""
    response = client.post(
        "/api/matching/evaluate/information",
        json={
            "user_answer": "two four eight seven two two three four two eight",
            "expected_value": "248-722-3428",
            "field_name": "phone_number",
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_correct"] is True
    assert data["confidence"] == 1.0


def test_evaluate_word_finding(client):
    """Test the word-finding evaluation endpoint."""
    response = client.post(
        "/api/matching/evaluate/word-finding",
        json={
            "user_answer": "That's a broom",
            "expected_name": "broom",
            "alternatives": ["sweeper"],
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_correct"] is True


def test_extract_answer(client):
    """Test the answer extraction endpoint."""
    response = client.post(
        "/api/matching/extract-answer",
        json={"transcript": "I think it's a dog"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "dog"


def test_evaluate_name_with_settings(client):
    """Test name evaluation with custom accommodation settings."""
    response = client.post(
        "/api/matching/evaluate/name",
        json={
            "user_answer": "John",
            "expected_name": "John Smith",
            "settings": {
                "match_first_name_only": False,
                "match_partial_substring": False,
                "match_word_overlap": False,
                "match_stop_word_filtering": False,
                "match_synonyms": False,
                "match_acceptable_alternatives": False,
            }
        }
    )
    assert response.status_code == 200
    data = response.json()
    # With all matching disabled except exact, "John" != "John Smith"
    assert data["is_correct"] is False


def test_evaluate_information_date(client):
    """Test date matching via information endpoint."""
    response = client.post(
        "/api/matching/evaluate/information",
        json={
            "user_answer": "Jan 15th",
            "expected_value": "January 15",
            "field_name": "date_of_birth",
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_correct"] is True
