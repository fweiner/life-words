"""Life Words Question-Based Recall service."""
import random
from typing import List, Dict, Any, Optional
from fastapi import HTTPException
from app.core.database import SupabaseClient
from app.services.utils import verify_session
from app.models.life_words_questions import (
    GeneratedQuestion,
    QuestionType,
    LifeWordsQuestionSessionCreate,
    LifeWordsQuestionResponseCreate,
)

MIN_CONTACTS_REQUIRED = 2

# Mapping of stored relationship values to acceptable spoken alternatives
RELATIONSHIP_ALTERNATIVES = {
    "child": ["child", "son", "daughter", "kid", "my child", "my son", "my daughter"],
    "grandchild": ["grandchild", "grandson", "granddaughter", "grandkid", "my grandchild", "my grandson", "my granddaughter"],
    "parent": ["parent", "mother", "father", "mom", "dad", "my parent", "my mother", "my father", "my mom", "my dad"],
    "sibling": ["sibling", "brother", "sister", "my sibling", "my brother", "my sister"],
    "son": ["son", "my son", "child", "kid", "boy"],
    "daughter": ["daughter", "my daughter", "child", "kid", "girl"],
    "grandson": ["grandson", "my grandson", "grandchild", "grandkid"],
    "granddaughter": ["granddaughter", "my granddaughter", "grandchild", "grandkid"],
    "mother": ["mother", "mom", "mommy", "mama", "my mother", "my mom", "parent"],
    "father": ["father", "dad", "daddy", "papa", "my father", "my dad", "parent"],
    "brother": ["brother", "my brother", "sibling", "bro"],
    "sister": ["sister", "my sister", "sibling", "sis"],
    "spouse": ["spouse", "husband", "wife", "partner", "my spouse", "my husband", "my wife"],
    "partner": ["partner", "my partner", "spouse", "significant other"],
    "friend": ["friend", "my friend", "buddy", "pal"],
    "pet": ["pet", "my pet", "dog", "cat", "animal"],
    "caregiver": ["caregiver", "my caregiver", "helper", "aide", "nurse"],
    "neighbor": ["neighbor", "my neighbor"],
    "other": ["other"],
}

# Stop words to filter out when comparing significant words
STOP_WORDS = {
    "a", "an", "the",
    "in", "on", "at", "to", "for", "of", "with", "by", "from", "up", "down",
    "into", "onto", "upon", "out", "over", "under", "through", "during",
    "and", "or", "but", "so", "yet", "nor",
    "i", "me", "my", "we", "us", "our", "you", "your", "he", "him", "his",
    "she", "her", "it", "its", "they", "them", "their", "who", "whom",
    "is", "are", "was", "were", "be", "been", "being", "am",
    "do", "does", "did", "doing", "done",
    "have", "has", "had", "having",
    "go", "goes", "went", "going", "gone",
    "get", "gets", "got", "getting",
    "see", "sees", "saw", "seeing", "seen",
    "come", "comes", "came", "coming",
    "take", "takes", "took", "taking", "taken",
    "make", "makes", "made", "making",
    "know", "knows", "knew", "knowing", "known",
    "think", "thinks", "thought", "thinking",
    "say", "says", "said", "saying",
    "like", "likes", "liked", "liking",
    "want", "wants", "wanted", "wanting",
    "can", "could", "will", "would", "shall", "should", "may", "might", "must",
    "very", "really", "just", "also", "too", "always", "never", "often",
    "sometimes", "usually", "when", "where", "why", "how", "there", "here",
    "that", "this", "these", "those", "what", "which",
    "all", "each", "every", "some", "any", "no", "not",
    "as", "if", "then", "than", "because", "while", "about",
}

# Synonym groups for semantic matching
SYNONYM_GROUPS = [
    {"daughter", "girl", "child", "kid"},
    {"son", "boy", "child", "kid"},
    {"spouse", "husband", "wife", "partner"},
    {"grandchild", "grandkid", "grandson", "granddaughter"},
    {"parent", "mom", "dad", "mother", "father"},
    {"sibling", "brother", "sister"},
    {"friend", "buddy", "pal", "companion"},
    {"caregiver", "helper", "aide", "nurse"},
    {"outgoing", "social", "extroverted", "friendly", "sociable", "talkative"},
    {"reserved", "quiet", "shy", "introverted", "private"},
    {"optimistic", "positive", "cheerful", "upbeat", "hopeful"},
    {"cautious", "careful", "prudent", "wary"},
    {"friendly", "kind", "nice", "warm", "caring", "loving", "sweet"},
    {"energetic", "active", "lively", "spirited", "dynamic"},
    {"calm", "peaceful", "relaxed", "mellow", "easygoing", "laid back"},
    {"funny", "humorous", "witty", "hilarious", "comedic"},
    {"smart", "intelligent", "clever", "bright", "wise"},
    {"generous", "giving", "charitable", "kind"},
    {"patient", "understanding", "tolerant"},
    {"hardworking", "diligent", "dedicated", "industrious"},
    {"home", "house", "my place", "their place", "residence"},
    {"church", "temple", "synagogue", "mosque", "place of worship"},
    {"work", "office", "job", "workplace"},
    {"school", "class", "college", "university"},
    {"park", "playground", "outside", "outdoors"},
    {"store", "shop", "market", "mall"},
    {"restaurant", "diner", "cafe", "eatery"},
    {"hospital", "clinic", "doctor", "medical"},
]


def get_relationship_alternatives(relationship: str) -> List[str]:
    """Get acceptable alternative answers for a relationship value."""
    rel_lower = relationship.lower()
    if rel_lower in RELATIONSHIP_ALTERNATIVES:
        return RELATIONSHIP_ALTERNATIVES[rel_lower]
    return [relationship.lower(), relationship.title(), relationship]


def extract_significant_words(text: str) -> set:
    """Extract significant words by removing stop words."""
    words = set(text.lower().split())
    return words - STOP_WORDS


def find_synonym_match(word1: str, word2: str) -> bool:
    """Check if two words are synonyms based on our groups."""
    w1 = word1.lower().strip()
    w2 = word2.lower().strip()
    for group in SYNONYM_GROUPS:
        if w1 in group and w2 in group:
            return True
    return False


def words_are_similar(user_words: set, expected_words: set) -> tuple[bool, float]:
    """Check if word sets are semantically similar using synonyms."""
    if not user_words or not expected_words:
        return False, 0.0

    matches = 0
    for uw in user_words:
        for ew in expected_words:
            if uw == ew or find_synonym_match(uw, ew):
                matches += 1
                break

    score = matches / max(len(user_words), len(expected_words))
    return score >= 0.5, score


def evaluate_answer(
    user_answer: str,
    expected: str,
    acceptable: List[str],
    settings: Optional[dict] = None
) -> tuple[bool, bool, float]:
    """
    Evaluate if user's answer matches expected.
    Returns (is_correct, is_partial, correctness_score)

    Matching strategies (in order, can be toggled via settings):
    1. Exact match (always enabled)
    2. Acceptable alternatives (match_acceptable_alternatives)
    3. First name only (match_first_name_only)
    4. Substring containment (match_partial_substring)
    5. Word overlap (match_word_overlap)
    6. Stop word filtering (match_stop_word_filtering)
    7. Synonym matching (match_synonyms)
    """
    if not user_answer:
        return False, False, 0.0

    if settings is None:
        settings = {}
    use_acceptable = settings.get("match_acceptable_alternatives", True)
    use_partial = settings.get("match_partial_substring", True)
    use_word_overlap = settings.get("match_word_overlap", True)
    use_stop_words = settings.get("match_stop_word_filtering", True)
    use_synonyms = settings.get("match_synonyms", True)
    use_first_name = settings.get("match_first_name_only", True)

    user_lower = user_answer.lower().strip()
    expected_lower = expected.lower().strip()

    # 1. Exact match
    if user_lower == expected_lower:
        return True, False, 1.0

    # 2. Acceptable alternatives
    if use_acceptable:
        for alt in acceptable:
            if alt and user_lower == alt.lower():
                return True, False, 1.0

    # 3. First name only
    if use_first_name and " " in expected:
        first_name = expected.split()[0].lower()
        if user_lower == first_name:
            return True, True, 0.9

    # 4. Substring containment
    if use_partial:
        if expected_lower in user_lower or user_lower in expected_lower:
            return True, True, 0.8

    # 5. Word overlap
    user_words = set(user_lower.split())
    expected_words = set(expected_lower.split())

    if use_word_overlap:
        common = user_words & expected_words
        if common:
            score = len(common) / max(len(user_words), len(expected_words))
            if score >= 0.5:
                return True, True, score

    # 6. Stop word filtering
    if use_stop_words:
        user_significant = extract_significant_words(user_lower)
        expected_significant = extract_significant_words(expected_lower)
        if user_significant and expected_significant:
            significant_common = user_significant & expected_significant
            if significant_common:
                score = len(significant_common) / max(len(user_significant), len(expected_significant))
                if score >= 0.3 or len(significant_common) >= 1:
                    return True, True, max(0.7, score)

    # 7. Synonym matching
    if use_synonyms:
        is_similar, similarity_score = words_are_similar(user_words, expected_words)
        if is_similar:
            return True, True, similarity_score

        if use_stop_words:
            user_significant = extract_significant_words(user_lower)
            expected_significant = extract_significant_words(expected_lower)
            if user_significant and expected_significant:
                is_similar_sig, similarity_score_sig = words_are_similar(user_significant, expected_significant)
                if is_similar_sig:
                    return True, True, similarity_score_sig

        for uw in user_words:
            for ew in expected_words:
                if find_synonym_match(uw, ew):
                    return True, True, 0.7

    return False, False, 0.0


def generate_questions_for_contacts(contacts: List[Dict[str, Any]]) -> List[GeneratedQuestion]:
    """Generate 5 questions using data from the provided contacts."""
    questions = []
    if len(contacts) < 2:
        return questions

    shuffled = contacts.copy()
    random.shuffle(shuffled)

    # Q1: Relationship recall
    c1 = shuffled[0]
    relationship = c1["relationship"]
    questions.append(GeneratedQuestion(
        contact_id=c1["id"],
        contact_name=c1["name"],
        contact_photo_url=c1["photo_url"],
        question_type=QuestionType.RELATIONSHIP,
        question_text=f"What is {c1['name']}'s relationship to you?",
        expected_answer=relationship,
        acceptable_answers=get_relationship_alternatives(relationship),
    ))

    # Q2: Association/Context
    c2 = shuffled[1] if len(shuffled) > 1 else shuffled[0]
    location = c2.get("location_context") or c2.get("association") or "at home"
    questions.append(GeneratedQuestion(
        contact_id=c2["id"],
        contact_name=c2["name"],
        contact_photo_url=c2["photo_url"],
        question_type=QuestionType.ASSOCIATION,
        question_text=f"Where do you usually see {c2['name']}?",
        expected_answer=location,
        acceptable_answers=[location.lower()] if location else [],
    ))

    # Q3: Interests
    c3 = shuffled[0]
    interests = c3.get("interests") or "spending time together"
    questions.append(GeneratedQuestion(
        contact_id=c3["id"],
        contact_name=c3["name"],
        contact_photo_url=c3["photo_url"],
        question_type=QuestionType.INTERESTS,
        question_text=f"What does {c3['name']} enjoy doing?",
        expected_answer=interests,
        acceptable_answers=[interests.lower()] if interests else [],
    ))

    # Q4: Personality
    c4 = shuffled[1] if len(shuffled) > 1 else shuffled[0]
    personality = c4.get("personality") or c4.get("description") or "kind and caring"
    questions.append(GeneratedQuestion(
        contact_id=c4["id"],
        contact_name=c4["name"],
        contact_photo_url=c4["photo_url"],
        question_type=QuestionType.PERSONALITY,
        question_text=f"How would you describe {c4['name']}'s personality?",
        expected_answer=personality,
        acceptable_answers=[personality.lower()] if personality else [],
    ))

    # Q5: Name from description (reverse recall)
    c5 = None
    hint = None
    for contact in shuffled:
        possible_hint = contact.get("interests") or contact.get("description") or contact.get("personality")
        if possible_hint:
            c5 = contact
            hint = possible_hint
            break

    if c5 and hint:
        relationship = c5["relationship"]
        hint_lower = hint.lower().strip()
        first_word = hint_lower.split()[0] if hint_lower else ""
        if hint_lower.startswith(("loves", "enjoys", "likes", "is ")):
            hint = hint[0].lower() + hint[1:]
        elif first_word.endswith("ing"):
            hint = f"loves {hint[0].lower() + hint[1:]}"
        else:
            hint = f"loves {hint}"
        questions.append(GeneratedQuestion(
            contact_id=c5["id"],
            contact_name=c5["name"],
            contact_photo_url=c5["photo_url"],
            question_type=QuestionType.NAME_FROM_DESC,
            question_text=f"Who is your {relationship} who {hint}?",
            expected_answer=c5["name"],
            acceptable_answers=[
                c5["name"].lower(),
                c5["name"].split()[0].lower() if " " in c5["name"] else c5["name"].lower(),
                c5.get("nickname", "").lower() if c5.get("nickname") else "",
            ],
        ))

    return questions


class LifeWordsQuestionService:
    """Service for Life Words Question-Based Recall sessions."""

    def __init__(self, db: SupabaseClient):
        self.db = db

    async def create_session(
        self, user_id: str, session_data: LifeWordsQuestionSessionCreate
    ) -> Dict[str, Any]:
        """Create a new question-based session and generate questions."""
        if session_data.contact_ids:
            contacts = await self.db.query(
                "personal_contacts",
                select="*",
                filters={"user_id": user_id, "is_active": True}
            )
            contacts = [c for c in contacts if c["id"] in session_data.contact_ids]
        else:
            contacts = await self.db.query(
                "personal_contacts",
                select="*",
                filters={"user_id": user_id, "is_active": True}
            )

        if not contacts or len(contacts) < MIN_CONTACTS_REQUIRED:
            raise HTTPException(
                status_code=400,
                detail=f"At least {MIN_CONTACTS_REQUIRED} contacts required"
            )

        contact_ids = [c["id"] for c in contacts]

        session = await self.db.insert(
            "life_words_question_sessions",
            {
                "user_id": user_id,
                "contact_ids": contact_ids,
                "is_completed": False,
                "total_questions": 5,
                "total_correct": 0,
                "average_response_time": 0,
                "average_clarity_score": 0,
            }
        )

        questions = generate_questions_for_contacts(contacts)

        return {
            "session": session[0],
            "questions": [q.model_dump() for q in questions],
            "contacts": contacts,
        }

    async def get_session(self, session_id: str, user_id: str) -> Dict[str, Any]:
        """Get question session with responses."""
        session = await verify_session(
            self.db, "life_words_question_sessions", session_id, user_id
        )

        responses = await self.db.query(
            "life_words_question_responses",
            select="*",
            filters={"session_id": session_id},
            order="created_at"
        )

        contacts = await self.db.query(
            "personal_contacts",
            select="*",
            filters={"user_id": user_id}
        )
        session_contacts = [c for c in contacts if c["id"] in session["contact_ids"]]

        return {
            "session": session,
            "responses": responses or [],
            "contacts": session_contacts,
        }

    async def save_response(
        self, session_id: str, user_id: str,
        response_data: LifeWordsQuestionResponseCreate
    ) -> Dict[str, Any]:
        """Save a response to a question."""
        await verify_session(
            self.db, "life_words_question_sessions", session_id, user_id
        )

        response = await self.db.insert(
            "life_words_question_responses",
            {
                "session_id": session_id,
                "user_id": user_id,
                "contact_id": response_data.contact_id,
                "question_type": response_data.question_type,
                "question_text": response_data.question_text,
                "expected_answer": response_data.expected_answer,
                "user_answer": response_data.user_answer,
                "is_correct": response_data.is_correct,
                "is_partial": response_data.is_partial,
                "response_time": response_data.response_time,
                "clarity_score": response_data.clarity_score,
                "correctness_score": response_data.correctness_score,
            }
        )
        return {"response": response[0]}

    async def complete_session(self, session_id: str, user_id: str) -> Dict[str, Any]:
        """Complete a question session and calculate statistics."""
        await verify_session(
            self.db, "life_words_question_sessions", session_id, user_id
        )

        responses = await self.db.query(
            "life_words_question_responses",
            select="*",
            filters={"session_id": session_id}
        )
        if not responses:
            raise HTTPException(status_code=400, detail="No responses found")

        total_correct = sum(1 for r in responses if r["is_correct"])
        total_partial = sum(1 for r in responses if r["is_partial"] and not r["is_correct"])

        response_times = [r["response_time"] for r in responses if r["response_time"]]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0

        clarity_scores = [r["clarity_score"] for r in responses if r["clarity_score"] is not None]
        avg_clarity = sum(clarity_scores) / len(clarity_scores) if clarity_scores else 0

        correctness_scores = [r["correctness_score"] for r in responses if r["correctness_score"] is not None]
        avg_correctness = sum(correctness_scores) / len(correctness_scores) if correctness_scores else 0

        statistics = {
            "total_questions": len(responses),
            "total_correct": total_correct,
            "total_partial": total_partial,
            "accuracy_percentage": round((total_correct / len(responses)) * 100, 1),
            "average_response_time_ms": round(avg_response_time, 0),
            "average_clarity_score": round(avg_clarity, 2),
            "average_correctness_score": round(avg_correctness, 2),
            "by_question_type": {},
        }

        for r in responses:
            qt = str(r["question_type"])
            if qt not in statistics["by_question_type"]:
                statistics["by_question_type"][qt] = {"correct": 0, "total": 0, "avg_time": 0}
            statistics["by_question_type"][qt]["total"] += 1
            if r["is_correct"]:
                statistics["by_question_type"][qt]["correct"] += 1

        updated = await self.db.update(
            "life_words_question_sessions",
            {"id": session_id},
            {
                "is_completed": True,
                "completed_at": "now()",
                "total_correct": total_correct,
                "average_response_time": round(avg_response_time, 2),
                "average_clarity_score": round(avg_clarity, 2),
                "statistics": statistics,
            }
        )

        return {"session": updated, "statistics": statistics}
