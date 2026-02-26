"""Pydantic models for request/response schemas.

Backward-compatible re-export file. All models are defined in per-domain
modules and re-exported here so existing imports continue to work.
"""
# Auth
from app.models.auth import (  # noqa: F401
    UserSignup,
    UserLogin,
    UserResponse,
    TokenResponse,
)

# Profile
from app.models.profile import (  # noqa: F401
    ProfileUpdate,
    ProfileResponse,
)

# Treatment
from app.models.treatment import (  # noqa: F401
    TreatmentSessionCreate,
    TreatmentSessionUpdate,
    TreatmentSessionResponse,
    TreatmentResultCreate,
    TreatmentResultResponse,
    UserProgressResponse,
    WordFindingSessionCreate,
    WordFindingResponse,
)

# Speech
from app.models.speech import (  # noqa: F401
    SpeechTranscribeResponse,
    TextToSpeechRequest,
)

# Life Words
from app.models.life_words import (  # noqa: F401
    PersonalContactCreate,
    PersonalContactUpdate,
    PersonalContactResponse,
    QuickAddContactCreate,
    LifeWordsStatusResponse,
    LifeWordsSessionCreate,
    LifeWordsSessionResponse,
    LifeWordsResponseCreate,
)

# Life Words Questions
from app.models.life_words_questions import (  # noqa: F401
    QuestionType,
    LifeWordsQuestionSessionCreate,
    LifeWordsQuestionSessionResponse,
    GeneratedQuestion,
    LifeWordsQuestionResponseCreate,
    LifeWordsQuestionResponseResponse,
)

# Life Words Information
from app.models.life_words_information import (  # noqa: F401
    InformationItem,
    InformationStatusResponse,
    LifeWordsInformationSessionCreate,
    LifeWordsInformationSessionResponse,
    LifeWordsInformationResponseCreate,
    LifeWordsInformationResponseResponse,
)

# Invites
from app.models.invites import (  # noqa: F401
    ContactInviteCreate,
    ContactInviteResponse,
    InviteVerifyResponse,
    InviteSubmitRequest,
    InviteSubmitResponse,
)

# Messaging
from app.models.messaging import (  # noqa: F401
    MessageCreate,
    PublicMessageCreate,
    MessageResponse,
    ConversationSummary,
    MessagingTokenResponse,
    MessagingTokenVerifyResponse,
)

# Items
from app.models.items import (  # noqa: F401
    PersonalItemCreate,
    PersonalItemUpdate,
    PersonalItemResponse,
    QuickAddItemCreate,
)

# Matching
from app.models.matching import (  # noqa: F401
    MatchSettings,
    NameMatchRequest,
    NameMatchResponse,
    QuestionMatchRequest,
    QuestionMatchResponse,
    InformationMatchRequest,
    InformationMatchResponse,
    WordFindingMatchRequest,
    WordFindingMatchResponse,
    ExtractAnswerRequest,
    ExtractAnswerResponse,
)

# Admin
from app.models.admin import (  # noqa: F401
    AdminUserStats,
    AdminDeleteResponse,
    AdminCreateUser,
    AdminCreateUserResponse,
    AdminUpdateUser,
    AdminUpdateUserResponse,
    AdminToggleUserResponse,
    ErrorLogResponse,
    ErrorLogListResponse,
    ResolveRequest,
)

# Stripe
from app.models.stripe import (  # noqa: F401
    CheckoutRequest,
    CheckoutResponse,
    PortalResponse,
    SubscriptionStatusResponse,
)

# STM
from app.models.stm import (  # noqa: F401
    STMGroceryItemResponse,
    STMSessionCreate,
    STMSessionResponse,
    STMTrialCreate,
    STMTrialResponse,
    STMRecallAttemptCreate,
    STMRecallAttemptResponse,
    STMCompleteTrialRequest,
    STMProgressResponse,
    STMSessionListResponse,
)
