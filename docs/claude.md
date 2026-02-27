# Life Words Application - Technical Documentation

This document provides comprehensive technical information about the Life Words application for AI assistants like Claude.

## Development Environment

**Operating System**: Windows 11

**Important Notes for AI Assistants**:
- This project is developed on Windows
- All PowerShell commands must be provided as **single-line commands**
- Multi-line PowerShell commands will fail when copy-pasted
- Use semicolons or proper continuation where needed, but keep commands on one line

**Example**:
```powershell
# ✅ CORRECT - Single line
[Environment]::SetEnvironmentVariable("Path", [Environment]::GetEnvironmentVariable("Path", "User") + ";C:\Users\weine\.local\bin", "User")

# ❌ WRONG - Multi-line (will fail when pasted)
[Environment]::SetEnvironmentVariable(
    "Path",
    [Environment]::GetEnvironmentVariable("Path", "User") + ";C:\Users\weine\.local\bin",
    "User"
)
```

## Project Overview

**Purpose**: A web-based cognitive and memory treatment application for users 65+ years old with cognitive challenges.

**Target Users**: Elderly users (65+) with cognitive and memory problems requiring:
- Large, readable fonts
- High accessibility standards (WCAG AAA)
- Simple, intuitive interfaces
- Speech-based interaction capabilities

## Architecture

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    User's Browser                         │
│              (words.parrotsoftware.com)                     │
│                                                           │
│  ┌─────────────────────────────────────────────────┐    │
│  │         Next.js 14+ (App Router)                │    │
│  │   - React with TypeScript                        │    │
│  │   - Tailwind CSS + shadcn/ui                    │    │
│  │   - Web Speech API / MediaRecorder              │    │
│  └──────────────┬──────────────────────────────────┘    │
└────────────────┼───────────────────────────────────────┘
                 │
                 │ HTTPS/REST
                 │
    ┌────────────┼────────────┬──────────────────┐
    │            │            │                  │
    ▼            ▼            ▼                  ▼
┌─────────┐ ┌─────────┐ ┌──────────┐  ┌──────────────┐
│Supabase │ │ FastAPI │ │  Google  │  │    OpenAI    │
│         │ │ Backend │ │  Cloud   │  │   GPT-4o-    │
│- Auth   │ │(Cloud   │ │  Speech  │  │    mini      │
│- DB     │ │ Run)    │ │  APIs    │  │              │
│- Storage│ │         │ │          │  │              │
└─────────┘ └─────────┘ └──────────┘  └──────────────┘
```

### Technology Stack

**Frontend**:
- Framework: Next.js 14+ with App Router
- Language: TypeScript
- Styling: Tailwind CSS
- UI Components: shadcn/ui
- State Management: React hooks + Supabase realtime
- Speech: Web Speech API / MediaRecorder API

**Backend**:
- Framework: FastAPI (Python 3.12+)
- Package Manager: uv (not pip)
- Async: uvicorn with async/await patterns
- Validation: Pydantic v2
- AI: OpenAI SDK with GPT-4o-mini

**Database & Auth**:
- Platform: Supabase (PostgreSQL + Auth + Storage)
- Project ID: nnvqtxwobvyitqbsdskc
- Auth Method: Email/password only
- Keys: Publishable (anon) + Secret (service_role)

**External Services**:
- Email: Resend (transactional emails)
- Speech-to-Text: Google Cloud Speech-to-Text API
- Text-to-Speech: Google Cloud Text-to-Speech API
- AI: OpenAI GPT-4o-mini

**Hosting**:
- Platform: Google Cloud Run (serverless containers)
- Frontend: `treatment-web` service
- Backend: `treatment-api` service
- Domain: words.parrotsoftware.com (frontend), api.parrotsoftware.com (backend)
- DNS: GoDaddy

**CI/CD**:
- Platform: GitHub Actions
- Trigger: Release tags (v*)
- Deployment: Automated to Cloud Run

### Design Patterns

**1. Thin Client Architecture**:
- Frontend: Minimal business logic, primarily UI/UX
- Backend: All business logic, data validation, and processing
- Rationale: Easier maintenance, better security, centralized logic

**2. Service Layer Pattern (Backend)**:
```
Router (thin) → Service (business logic) → Database
```
- **Routers** (`app/routers/*`): HTTP endpoints, request/response handling
- **Services** (`app/services/*`): Business logic, data processing
- **Core** (`app/core/*`): Shared utilities (database, auth, config)

**3. Route Groups (Frontend)**:
```
app/
├── (auth)/          # Public routes (login, signup)
├── (dashboard)/     # Protected routes (treatments, progress)
└── layout.tsx       # Root layout
```

## Directory Structure

```
life-words/
├── frontend/                       # Next.js application
│   ├── app/
│   │   ├── (auth)/                # Auth routes (login, signup)
│   │   │   ├── login/
│   │   │   └── signup/
│   │   ├── (dashboard)/           # Protected routes
│   │   │   ├── layout.tsx        # Dashboard layout with nav
│   │   │   ├── page.tsx          # Dashboard home
│   │   │   ├── treatments/       # Treatment apps
│   │   │   │   ├── word-finding/
│   │   │   │   ├── life-words/
│   │   │   │   └── ...           # Other treatment apps
│   │   │   ├── progress/         # Progress tracking
│   │   │   └── settings/
│   │   ├── layout.tsx            # Root layout
│   │   └── globals.css
│   ├── components/
│   │   ├── ui/                   # shadcn/ui components
│   │   ├── auth/                 # Auth components
│   │   ├── treatments/           # Treatment components
│   │   └── Navigation.tsx
│   ├── lib/
│   │   ├── supabase.ts          # Supabase client
│   │   ├── google-speech.ts     # Speech API client
│   │   └── utils.ts
│   ├── middleware.ts            # Auth middleware
│   └── next.config.ts
│
├── backend/                       # FastAPI application
│   ├── app/
│   │   ├── main.py              # FastAPI app entry
│   │   ├── config.py            # Settings (Pydantic)
│   │   ├── core/
│   │   │   ├── database.py      # Supabase client
│   │   │   ├── auth.py          # JWT verification
│   │   │   └── dependencies.py  # FastAPI dependencies
│   │   ├── routers/
│   │   │   ├── auth.py          # Auth endpoints
│   │   │   ├── treatments.py    # Treatment endpoints
│   │   │   └── results.py       # Progress endpoints
│   │   ├── services/
│   │   │   ├── auth_service.py
│   │   │   ├── treatment_service.py
│   │   │   ├── speech_service.py
│   │   │   └── ai_service.py
│   │   └── models/
│   │       └── schemas.py       # Pydantic models
│   ├── pyproject.toml           # uv dependencies
│   ├── Dockerfile               # Production container
│   └── .env.example
│
├── docs/
│   ├── setup/                   # Step-by-step setup guides
│   │   ├── 01-openai-setup.md
│   │   ├── 02-gcp-setup.md
│   │   ├── 03-resend-setup.md
│   │   ├── 04-github-secrets.md
│   │   ├── 05-domain-deployment.md
│   │   └── 06-supabase-setup.md
│   └── claude.md                # This file
│
├── .github/
│   └── workflows/
│       └── deploy-production.yml
│
├── .vscode/
│   └── launch.json             # Debug configurations
│
├── .gitignore
├── .env.example
└── README.md
```

## Database Schema

### Tables

#### 1. profiles
Extends `auth.users` with additional user information.

```sql
CREATE TABLE public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    full_name TEXT,
    date_of_birth DATE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Indexes**:
- `profiles_email_idx` on `email`

**RLS Policies**:
- Users can view/update/insert their own profile

**Trigger**:
- Auto-creates profile when user signs up

#### 2. treatment_sessions
Records of individual treatment sessions.

```sql
CREATE TABLE public.treatment_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    treatment_type TEXT NOT NULL,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    data JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Treatment Types**:
- `word_finding` - Word finding exercises
- `life_words` - Personal contacts/items naming practice
- `short_term_memory` - Memory exercises (placeholder)
- ...more types (to be defined)

**Indexes**:
- `treatment_sessions_user_id_idx`
- `treatment_sessions_treatment_type_idx`
- `treatment_sessions_created_at_idx`

**RLS Policies**:
- Users can view/insert/update their own sessions

#### 3. treatment_results
Results from completed sessions.

```sql
CREATE TABLE public.treatment_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES treatment_sessions(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    score INTEGER,
    details JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Indexes**:
- `treatment_results_session_id_idx`
- `treatment_results_user_id_idx`
- `treatment_results_created_at_idx`

**RLS Policies**:
- Users can view/insert their own results

#### 4. user_progress
Aggregated progress statistics per treatment type.

```sql
CREATE TABLE public.user_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    treatment_type TEXT NOT NULL,
    total_sessions INTEGER DEFAULT 0,
    average_score NUMERIC,
    last_session_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, treatment_type)
);
```

**Indexes**:
- `user_progress_user_id_idx`
- `user_progress_treatment_type_idx`

**RLS Policies**:
- Users can view/update/insert their own progress

### Storage Buckets

1. **treatment-images** (public):
   - Purpose: Public images for UI (icons, illustrations)
   - Access: Anyone can read

2. **user-uploads** (private):
   - Purpose: User-generated content (audio recordings, etc.)
   - Access: Users can only access their own files
   - Path structure: `user-uploads/{user_id}/{filename}`

## API Endpoints

### Authentication (`/api/auth`)

```
POST   /api/auth/signup       # Create new user account
POST   /api/auth/login        # Sign in with email/password
POST   /api/auth/logout       # Sign out
GET    /api/auth/me           # Get current user info
```

### Treatments (`/api/treatments`)

```
POST   /api/treatments/sessions           # Create treatment session
GET    /api/treatments/sessions           # Get user's sessions
GET    /api/treatments/sessions/:id       # Get specific session
```

### Speech (`/api/speech`)

```
POST   /api/speech/transcribe     # Convert speech to text
POST   /api/speech/synthesize     # Convert text to speech
```

### Results (`/api/results`)

```
GET    /api/results/user/:userId          # Get all user results
GET    /api/results/progress/:userId      # Get aggregated progress
GET    /api/results/treatment/:type       # Get results by treatment type
```

## Authentication Flow

### User Signup

1. User fills signup form (email, password, full_name)
2. Frontend calls Supabase `signUp()`
3. Supabase:
   - Creates user in `auth.users`
   - Triggers `handle_new_user()` function
   - Function creates profile in `public.profiles`
   - Sends confirmation email via Resend
4. User clicks email link to confirm
5. User can now log in

### User Login

1. User enters email/password
2. Frontend calls Supabase `signInWithPassword()`
3. Supabase validates credentials
4. Returns session with JWT token
5. Frontend stores session in cookies
6. All API requests include JWT in Authorization header

### Backend Auth Verification

```python
# Pseudo-code
def verify_token(token: str) -> User:
    # Decode JWT using Supabase public key
    # Verify signature
    # Extract user_id
    # Return user object
```

## Speech Integration

### Speech-to-Text Flow

1. **Frontend**: Record audio using MediaRecorder API
   - Format: WebM or other supported format
   - Duration: 1-30 seconds

2. **Send to Backend**:
   ```typescript
   const response = await fetch('/api/speech/transcribe', {
     method: 'POST',
     body: audioBlob
   });
   ```

3. **Backend Processing**:
   ```python
   # app/services/speech_service.py
   async def speech_to_text(audio_bytes: bytes) -> str:
       client = speech.SpeechClient()
       audio = speech.RecognitionAudio(content=audio_bytes)
       config = speech.RecognitionConfig(
           encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
           sample_rate_hertz=48000,
           language_code="en-US"
       )
       response = client.recognize(config=config, audio=audio)
       return response.results[0].alternatives[0].transcript
   ```

4. **Return Text**: JSON response with transcribed text

### Text-to-Speech Flow

1. **Frontend Sends Text**:
   ```typescript
   const response = await fetch('/api/speech/synthesize', {
     method: 'POST',
     body: JSON.stringify({ text: "Hello world" })
   });
   ```

2. **Backend Processing**:
   ```python
   async def text_to_speech(text: str) -> bytes:
       client = texttospeech.TextToSpeechClient()
       synthesis_input = texttospeech.SynthesisInput(text=text)
       voice = texttospeech.VoiceSelectionParams(
           language_code="en-US",
           ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
       )
       audio_config = texttospeech.AudioConfig(
           audio_encoding=texttospeech.AudioEncoding.MP3
       )
       response = client.synthesize_speech(
           input=synthesis_input,
           voice=voice,
           audio_config=audio_config
       )
       return response.audio_content
   ```

3. **Return Audio**: Binary audio data
4. **Frontend**: Play audio using HTML5 Audio API

## Accessibility Implementation

### WCAG AAA Standards

- **Color Contrast**: 7:1 for normal text, 4.5:1 for large text
- **Font Sizes**: Base 18px minimum (larger than standard 16px)
- **Touch Targets**: Minimum 44x44px for all interactive elements
- **Keyboard Navigation**: Full keyboard support, visible focus indicators
- **Screen Readers**: ARIA labels on all interactive elements
- **Semantic HTML**: Proper use of header, main, nav, section, article tags

### Design System

**Colors** (Blue Theme):
```css
:root {
  --color-primary: #2563eb;      /* blue-600 */
  --color-secondary: #60a5fa;    /* blue-400 */
  --color-accent: #0ea5e9;       /* sky-500 */
  --color-background: #f8fafc;   /* slate-50 */
  --color-text: #0f172a;         /* slate-900 */
  --color-text-muted: #475569;   /* slate-600 */
}
```

**Typography**:
- Base: 18px (1.125rem)
- Headings: 24px+ (1.5rem+)
- Line height: 1.6 (more readable)
- Font: System fonts (ui-sans-serif, system-ui)

**Spacing**:
- Touch targets: 44x44px minimum
- Padding: Generous (p-6, p-8 instead of p-4)
- Margins: Clear separation between sections

### Reduced Motion

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

## Environment Variables

### Frontend (.env.local)

```env
NEXT_PUBLIC_SUPABASE_URL=https://nnvqtxwobvyitqbsdskc.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=<publishable-key>
NEXT_PUBLIC_API_URL=http://localhost:8000  # or https://api.parrotsoftware.com
NEXT_PUBLIC_GOOGLE_CLOUD_API_KEY=<optional-for-client-side-speech>
RESEND_API_KEY=<for-server-actions>
```

### Backend (.env)

```env
SUPABASE_URL=https://nnvqtxwobvyitqbsdskc.supabase.co
SUPABASE_SECRET_KEY=<secret-key>
OPENAI_API_KEY=<openai-key>
GOOGLE_CLOUD_PROJECT=life-words-production
GOOGLE_APPLICATION_CREDENTIALS=gcp-runtime.json
RESEND_API_KEY=<resend-key>
ENVIRONMENT=development
ALLOWED_ORIGINS=http://localhost:3000,https://words.parrotsoftware.com
```

## Local Development

### Prerequisites

- Node.js 20+
- Python 3.12+
- uv (Python package manager)
- Git

### Setup

1. **Clone Repository**:
   ```bash
   git clone https://github.com/fweiner/life-words.git
   cd life-words
   ```

2. **Frontend Setup**:
   ```bash
   cd frontend
   npm install
   cp .env.local.example .env.local
   # Edit .env.local with your keys
   npm run dev  # Runs on http://localhost:3000
   ```

3. **Backend Setup**:
   ```bash
   cd backend
   uv sync
   cp .env.example .env
   # Edit .env with your keys
   uv run uvicorn app.main:app --reload  # Runs on http://localhost:8000
   ```

### VSCode Debugging

Use the compound configuration "Full Stack Debug" in `.vscode/launch.json` to debug both frontend and backend simultaneously.

## Deployment

### Triggering Deployment

1. Commit changes to `main` branch
2. Create a GitHub release with a version tag (e.g., `v1.0.1`)
3. GitHub Actions automatically builds and deploys

### Deployment Process

1. **GitHub Actions Workflow** (`.github/workflows/deploy-production.yml`):
   - Triggered by release creation
   - Builds Docker images for frontend and backend
   - Pushes to Google Artifact Registry
   - Deploys to Cloud Run

2. **Cloud Run Services**:
   - `treatment-web`: Next.js frontend
   - `treatment-api`: FastAPI backend
   - Auto-scaling: 0-10 instances
   - Region: us-central1

3. **Custom Domains**:
   - Frontend: https://words.parrotsoftware.com
   - Backend: https://api.parrotsoftware.com
   - SSL: Automatically provisioned by Cloud Run

## Cost Estimates

**Monthly costs for low traffic** (~1000 users, ~500 sessions/month):

- **Cloud Run**: $0-5 (free tier: 2M requests/month)
- **Supabase**: $0 (free tier sufficient)
- **Google Speech APIs**: $6-12
  - STT: ~$3-6 (60 min free, then $0.006/15s)
  - TTS: ~$3-6 ($4-16 per 1M characters)
- **OpenAI GPT-4o-mini**: $1-3 (very low cost)
- **Resend**: $0 (free tier: 3000 emails/month)

**Total**: ~$7-25/month for low traffic

## Troubleshooting

### Common Issues

**1. CORS Errors**:
- Verify `ALLOWED_ORIGINS` in backend includes frontend URL
- Check frontend is using correct API URL

**2. Authentication Errors**:
- Verify Supabase keys are correct (anon for frontend, secret for backend)
- Check JWT token is being sent in Authorization header
- Ensure user is confirmed (check email)

**3. Speech API Errors**:
- Verify Google Cloud credentials are set up correctly
- Check APIs are enabled in GCP
- Ensure service account has correct permissions

**4. Database Errors**:
- Verify RLS policies allow the operation
- Check user is authenticated
- Ensure foreign key constraints are satisfied

## Future Enhancements

1. **Implement 9 Remaining Treatment Apps**:
   - Word finding exercises
   - Short-term memory games
   - Pattern recognition
   - Sequential memory
   - Visual perception
   - Auditory processing
   - Problem solving
   - Attention training
   - Executive function exercises

2. **Advanced Features**:
   - Progress analytics with charts
   - Personalized difficulty adjustment
   - Caregiver dashboard
   - Multi-language support
   - Offline mode (PWA)
   - Mobile app (React Native)

3. **AI Enhancements**:
   - Personalized treatment recommendations
   - Adaptive difficulty using GPT-4o-mini
   - Voice analysis for cognitive assessment

## Contact & Support

- **Repository**: https://github.com/fweiner/life-words
- **Issues**: GitHub Issues
- **Documentation**: `docs/` directory
