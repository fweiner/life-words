"""Answer matching service for evaluating user responses across all practice types.

Ports matching logic from frontend (answerMatcher.ts, informationMatcher.ts,
settings.ts) into a single backend service. Also re-uses evaluate_answer from
the existing LifeWordsQuestionService for question-practice matching.
"""
import re
from typing import Dict, List, Optional, Tuple

# ============== Constants ==============

# Spoken number → digit mapping (used for phone, zip, date, number fields)
WORD_TO_NUMBER: Dict[str, str] = {
    "zero": "0", "oh": "0", "o": "0",
    "one": "1", "won": "1",
    "two": "2", "to": "2", "too": "2",
    "three": "3",
    "four": "4", "for": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8", "ate": "8",
    "nine": "9",
    "ten": "10",
    "eleven": "11",
    "twelve": "12",
    "thirteen": "13",
    "fourteen": "14",
    "fifteen": "15",
    "sixteen": "16",
    "seventeen": "17",
    "eighteen": "18",
    "nineteen": "19",
    "twenty": "20",
    "thirty": "30",
    "forty": "40",
    "fifty": "50",
    "sixty": "60",
    "seventy": "70",
    "eighty": "80",
    "ninety": "90",
    "hundred": "00",
}

# Month name/abbreviation → canonical name
MONTH_NAMES: Dict[str, str] = {
    "january": "january", "jan": "january",
    "february": "february", "feb": "february",
    "march": "march", "mar": "march",
    "april": "april", "apr": "april",
    "may": "may",
    "june": "june", "jun": "june",
    "july": "july", "jul": "july",
    "august": "august", "aug": "august",
    "september": "september", "sept": "september", "sep": "september",
    "october": "october", "oct": "october",
    "november": "november", "nov": "november",
    "december": "december", "dec": "december",
}

# Family-focused synonyms (used for name-practice matching)
SYNONYMS: Dict[str, List[str]] = {
    "dad": ["father", "daddy", "papa", "pop", "pa"],
    "father": ["dad", "daddy", "papa", "pop", "pa"],
    "mom": ["mother", "mommy", "mama", "ma"],
    "mother": ["mom", "mommy", "mama", "ma"],
    "grandma": ["grandmother", "granny", "nana", "gran"],
    "grandmother": ["grandma", "granny", "nana", "gran"],
    "grandpa": ["grandfather", "gramps", "granddad", "papa"],
    "grandfather": ["grandpa", "gramps", "granddad", "papa"],
    "wife": ["spouse", "partner"],
    "husband": ["spouse", "partner"],
    "kid": ["child", "son", "daughter"],
    "child": ["kid", "son", "daughter"],
    "home": ["house", "residence", "place"],
    "house": ["home", "residence", "place"],
    "nice": ["kind", "friendly", "good", "sweet"],
    "kind": ["nice", "friendly", "good", "sweet"],
    "happy": ["glad", "joyful", "cheerful"],
    "sad": ["unhappy", "upset", "down"],
    "big": ["large", "huge", "great"],
    "small": ["little", "tiny", "mini"],
    "old": ["elderly", "senior", "aged"],
    "young": ["youthful", "junior"],
    "friend": ["buddy", "pal", "mate"],
    "brother": ["bro", "sibling"],
    "sister": ["sis", "sibling"],
    "doctor": ["dr", "physician", "doc"],
    "mister": ["mr"],
    "missus": ["mrs", "ms"],
}

# Stop words for name-practice matching
STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "it", "this", "that", "these", "those",
    "i", "you", "he", "she", "we", "they", "my", "your", "his", "her", "our",
    "their", "when", "where", "who", "what", "which", "how", "why",
    "am", "are", "was", "were", "be", "been", "being", "have", "has", "had",
    "do", "does", "did", "will", "would", "could", "should", "may", "might",
    "must", "shall", "can", "just", "like", "so", "very", "really", "um", "uh",
}

# Phrase patterns for extracting answers from speech transcripts
PHRASE_PATTERNS = [
    re.compile(r"(?:that'?s|it'?s|this'?s|that is|it is|this is)\s+(?:a|an)\s+(.+)", re.I),
    re.compile(r"(?:that'?s|it'?s|this'?s|that is|it is|this is)\s+(.+)", re.I),
    re.compile(r"(?:it'?s|that'?s|this'?s)\s+(?:a|an)\s+(.+)", re.I),
    re.compile(r"(?:looks like|seems like|appears to be)\s+(?:a|an)?\s*(.+)", re.I),
    re.compile(r"(?:i think|i believe|i see)\s+(?:it'?s|that'?s|this'?s)?\s*(?:a|an)?\s*(.+)", re.I),
    re.compile(r"(?:i\s+(?:like|want|love|need|have|see|know|remember|recognize))\s+(?:a|an|the)?\s*(.+)", re.I),
    re.compile(r"(.+?)\s+(?:is|looks|seems|appears)\s+(?:good|nice|cool|great|fine|okay|ok)", re.I),
]

FILLER_WORDS = ["um", "uh", "er", "ah", "you know", "the", "a", "an"]


# ============== Pure utility functions ==============

def normalize(text: str) -> str:
    """Normalize a string: lowercase, trim, remove punctuation, collapse whitespace."""
    s = text.lower().strip()
    s = re.sub(r"[.,!?;:'\"]+", "", s)
    s = re.sub(r"\s+", " ", s)
    return s


def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate the Levenshtein (edit) distance between two strings."""
    a = normalize(s1)
    b = normalize(s2)
    if len(a) < len(b):
        a, b = b, a
    if len(b) == 0:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a):
        curr = [i + 1]
        for j, cb in enumerate(b):
            cost = 0 if ca == cb else 1
            curr.append(min(
                curr[j] + 1,       # insert
                prev[j + 1] + 1,   # delete
                prev[j] + cost,    # substitute
            ))
        prev = curr
    return prev[len(b)]


def is_plural_match(word1: str, word2: str) -> bool:
    """Check if two words are singular/plural variants of each other."""
    w1 = normalize(word1)
    w2 = normalize(word2)
    if w1 == w2:
        return True
    pairs = [
        (w1, w1 + "s"),
        (w1, w1 + "es"),
        (w1[:-1] if len(w1) > 1 else w1, w1),   # w1 might be plural (-s)
        (w1[:-2] if len(w1) > 2 else w1, w1),    # w1 might be plural (-es)
    ]
    for singular, plural in pairs:
        if singular == w2 or plural == w2:
            return True
    return False


def extract_digits(text: str) -> str:
    """Extract only digit characters from a string."""
    return re.sub(r"\D", "", text)


def convert_spoken_to_digits(text: str) -> str:
    """Convert spoken number words to digit string (e.g. 'five five five' → '555')."""
    words = normalize(text).split()
    result = ""
    for word in words:
        if word in WORD_TO_NUMBER:
            result += WORD_TO_NUMBER[word]
        elif word.isdigit():
            result += word
    return result


def extract_month(date_str: str) -> Optional[str]:
    """Extract canonical month name from a date string."""
    n = normalize(date_str)
    for variant, month in MONTH_NAMES.items():
        if variant in n:
            return month
    return None


def extract_day(date_str: str) -> Optional[str]:
    """Extract day number (1-31) from a date string."""
    m = re.search(r"\b(\d{1,2})(?:st|nd|rd|th)?\b", date_str)
    if m:
        return m.group(1)
    # Try spoken numbers
    for word in normalize(date_str).split():
        if word in WORD_TO_NUMBER:
            num = int(WORD_TO_NUMBER[word])
            if 1 <= num <= 31:
                return str(num)
    return None


def calculate_similarity(str1: str, str2: str) -> float:
    """Calculate Jaccard word-overlap similarity (0-1) between two strings."""
    s1 = normalize(str1)
    s2 = normalize(str2)
    if s1 == s2:
        return 1.0
    words1 = set(s1.split())
    words2 = set(s2.split())
    union = words1 | words2
    if not union:
        return 0.0
    intersection = words1 & words2
    return len(intersection) / len(union)


def remove_stop_words(text: str) -> str:
    """Remove stop words from text."""
    return " ".join(w for w in text.split() if w.lower() not in STOP_WORDS)


def get_synonyms(word: str) -> List[str]:
    """Get synonym list for a word."""
    return SYNONYMS.get(word.lower(), [])


def calculate_word_overlap(answer: str, expected: str) -> float:
    """Calculate fraction of expected words found in the answer."""
    answer_words = set(answer.lower().split())
    expected_words = expected.lower().split()
    if not expected_words:
        return 0.0
    matches = sum(1 for w in expected_words if w in answer_words)
    return matches / len(expected_words)


# ============== Matching functions by practice type ==============


def match_word_finding_answer(
    user_answer: str,
    expected_name: str,
    alternatives: Optional[List[str]] = None,
) -> bool:
    """
    Match a word-finding answer (image naming).

    Ports answerMatcher.ts: matchAnswer() logic.
    Priority: whole-word regex → exact → alternatives → plural → fuzzy.
    """
    if not user_answer or not expected_name:
        return False

    alternatives = alternatives or []
    normalized_user = normalize(user_answer)
    normalized_correct = normalize(expected_name)

    # 1. Whole-word regex match in user's utterance
    escaped = re.escape(normalized_correct)
    if re.search(rf"\b{escaped}\b", user_answer, re.I):
        return True
    for alt in alternatives:
        escaped_alt = re.escape(normalize(alt))
        if re.search(rf"\b{escaped_alt}\b", user_answer, re.I):
            return True

    # 2. Exact match
    if normalized_user == normalized_correct:
        return True
    for alt in alternatives:
        if normalized_user == normalize(alt):
            return True

    # 3. Plural/singular
    if is_plural_match(normalized_user, normalized_correct):
        return True
    for alt in alternatives:
        if is_plural_match(normalized_user, normalize(alt)):
            return True

    # 4. Fuzzy (Levenshtein)
    max_dist = 1 if len(normalized_correct) <= 5 else 2
    dist = levenshtein_distance(normalized_user, normalized_correct)
    if dist <= max_dist and len(normalized_user) >= len(normalized_correct) - 2:
        return True
    for alt in alternatives:
        n_alt = normalize(alt)
        alt_max = 1 if len(n_alt) <= 5 else 2
        if levenshtein_distance(normalized_user, n_alt) <= alt_max and len(normalized_user) >= len(n_alt) - 2:
            return True

    return False


def match_name_answer(
    user_answer: str,
    expected_name: str,
    nickname: Optional[str] = None,
    alternatives: Optional[List[str]] = None,
    settings=None,
) -> Tuple[bool, Optional[str]]:
    """
    Match a name-practice answer.

    Returns (is_correct, matched_via) where matched_via describes which
    strategy matched (e.g. 'exact', 'nickname', 'first_name', 'partial',
    'synonym', 'word_overlap').

    Ports settings.ts: matchAnswer() + session page: matchPersonalAnswer().
    """
    if not user_answer or not expected_name:
        return False, None

    # Accept Pydantic models or dicts
    if settings is not None and hasattr(settings, "model_dump"):
        settings = settings.model_dump()
    if settings is None:
        settings = {}
    use_alternatives = settings.get("match_acceptable_alternatives", True)
    use_partial = settings.get("match_partial_substring", True)
    use_word_overlap = settings.get("match_word_overlap", True)
    use_stop_words = settings.get("match_stop_word_filtering", True)
    use_synonyms = settings.get("match_synonyms", True)
    use_first_name = settings.get("match_first_name_only", True)

    answer_norm = normalize(user_answer)
    expected_norm = normalize(expected_name)

    # Apply stop-word filtering if enabled
    if use_stop_words:
        answer_filtered = remove_stop_words(answer_norm)
        expected_filtered = remove_stop_words(expected_norm)
    else:
        answer_filtered = answer_norm
        expected_filtered = expected_norm

    # 1. Exact match (always enabled)
    if answer_filtered == expected_filtered:
        return True, "exact"

    # 2. Nickname match
    if nickname:
        if answer_filtered == normalize(nickname):
            return True, "nickname"

    # 3. First name only
    if use_first_name and " " in expected_name:
        first_name = expected_norm.split()[0]
        if answer_filtered == first_name:
            return True, "first_name"
        # Also check if answer's first word matches expected first name
        answer_first = answer_filtered.split()[0] if answer_filtered else ""
        if answer_first == first_name:
            return True, "first_name"

    # 4. Acceptable alternatives
    alternatives = alternatives or []
    if use_alternatives and alternatives:
        for alt in alternatives:
            if answer_filtered == normalize(alt):
                return True, "alternative"

    # 5. Partial matching (contains)
    if use_partial:
        if expected_filtered in answer_filtered:
            return True, "partial"
        if answer_filtered in expected_filtered and len(answer_filtered) >= 2:
            return True, "partial"
        # Prefix match (e.g. "Ben" matches "Benjamin")
        if " " not in expected_norm:
            if expected_norm.startswith(answer_filtered) or answer_filtered.startswith(expected_norm):
                if len(answer_filtered) >= 2:
                    return True, "partial"

    # 6. Word overlap
    if use_word_overlap:
        overlap = calculate_word_overlap(answer_filtered, expected_filtered)
        if overlap >= 0.5:
            return True, "word_overlap"

    # 7. Synonym matching
    if use_synonyms:
        answer_words = answer_filtered.split()
        expected_words = expected_filtered.split()
        for aw in answer_words:
            for ew in expected_words:
                if aw == ew:
                    continue
                if aw in get_synonyms(ew):
                    return True, "synonym"

    return False, None


def match_question_answer(
    user_answer: str,
    expected: str,
    acceptable: Optional[List[str]] = None,
    settings=None,
) -> Tuple[bool, bool, float]:
    """
    Match a question-practice answer.

    Delegates to the existing evaluate_answer() from the question service.
    Returns (is_correct, is_partial, score).
    """
    # Accept Pydantic models or dicts
    if settings is not None and hasattr(settings, "model_dump"):
        settings = settings.model_dump()
    from app.services.life_words_question_service import evaluate_answer
    return evaluate_answer(user_answer, expected, acceptable or [], settings)


def match_phone_number(user_answer: str, expected: str) -> bool:
    """Match phone numbers by comparing digits (handles spoken numbers)."""
    if not user_answer or not expected:
        return False
    expected_digits = extract_digits(expected)
    user_digits = extract_digits(user_answer)
    if user_digits == expected_digits:
        return True
    spoken_digits = convert_spoken_to_digits(user_answer)
    if spoken_digits == expected_digits:
        return True
    # Combined: some digits typed, some spoken
    non_digit_part = re.sub(r"\d", "", user_answer)
    combined = extract_digits(user_answer) + convert_spoken_to_digits(non_digit_part)
    if combined == expected_digits:
        return True
    # Partial: last 4+ or 7+ digits match
    if len(user_digits) >= 4 and expected_digits.endswith(user_digits):
        return True
    if len(spoken_digits) >= 4 and expected_digits.endswith(spoken_digits):
        return True
    return False


def match_zip_code(user_answer: str, expected: str) -> bool:
    """Match zip codes by comparing digits (handles spoken numbers)."""
    if not user_answer or not expected:
        return False
    expected_digits = extract_digits(expected)
    user_digits = extract_digits(user_answer)
    spoken_digits = convert_spoken_to_digits(user_answer)
    return user_digits == expected_digits or spoken_digits == expected_digits


def match_number(user_answer: str, expected: str) -> bool:
    """Match number values (e.g. number of children)."""
    if not user_answer or not expected:
        return False
    try:
        expected_num = int(expected)
    except ValueError:
        return False
    # Direct parse
    try:
        if int(user_answer) == expected_num:
            return True
    except ValueError:
        pass
    # Spoken number conversion
    spoken_digits = convert_spoken_to_digits(user_answer)
    if spoken_digits:
        try:
            if int(spoken_digits) == expected_num:
                return True
        except ValueError:
            pass
    # Check if a number word in the answer maps to expected
    normalized_user = normalize(user_answer)
    for word, digit in WORD_TO_NUMBER.items():
        try:
            if word in normalized_user and int(digit) == expected_num:
                return True
        except ValueError:
            pass
    return False


def match_date(user_answer: str, expected: str) -> bool:
    """Match dates (e.g. 'January 15')."""
    if not user_answer or not expected:
        return False
    if normalize(user_answer) == normalize(expected):
        return True
    expected_month = extract_month(expected)
    expected_day = extract_day(expected)
    user_month = extract_month(user_answer)
    user_day = extract_day(user_answer)
    if expected_month and expected_day and user_month and user_day:
        return expected_month == user_month and expected_day == user_day
    # Month-only partial credit
    if expected_month and user_month and expected_month == user_month:
        return True
    return False


def match_text(user_answer: str, expected: str, threshold: float = 0.7) -> bool:
    """Match text fields with fuzzy matching."""
    if not user_answer or not expected:
        return False
    nu = normalize(user_answer)
    ne = normalize(expected)
    if nu == ne:
        return True
    if nu in ne or ne in nu:
        return True
    return calculate_similarity(user_answer, expected) >= threshold


def match_information_answer(
    user_answer: str,
    expected: str,
    field_name: str,
) -> Tuple[bool, float]:
    """
    Route to the correct field-specific matcher.

    Returns (is_correct, confidence).
    """
    if not user_answer or not expected:
        return False, 0.0

    if field_name == "phone_number":
        is_correct = match_phone_number(user_answer, expected)
    elif field_name == "address_zip":
        is_correct = match_zip_code(user_answer, expected)
    elif field_name == "number_of_children":
        is_correct = match_number(user_answer, expected)
    elif field_name == "date_of_birth":
        is_correct = match_date(user_answer, expected)
    else:
        is_correct = match_text(user_answer, expected)

    confidence = 1.0 if is_correct else calculate_similarity(user_answer, expected)
    return is_correct, confidence


def extract_answer(transcript: str) -> str:
    """
    Extract the most likely answer from a speech recognition transcript.

    Handles phrases like "That's a broom", "I think it's a pizza", etc.
    Ports answerMatcher.ts: extractAnswer().
    """
    cleaned = transcript.lower().strip()

    # Try phrase patterns
    for pattern in PHRASE_PATTERNS:
        m = pattern.match(cleaned)
        if m and m.group(1):
            extracted = m.group(1).strip()
            extracted = re.sub(r"[.,!?;:'\"]+$", "", extracted).strip()
            if extracted:
                return extracted

    # Remove filler words
    for filler in FILLER_WORDS:
        cleaned = re.sub(rf"\b{re.escape(filler)}\b", "", cleaned, flags=re.I)

    words = [w for w in cleaned.split() if w]
    if not words:
        return transcript.strip()

    # Return last 1-3 words
    last_words = " ".join(words[-3:])
    return last_words.strip() or transcript.strip()
