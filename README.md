# Life Words

A web-based cognitive and memory treatment application designed for users 65+ years old with cognitive challenges. Features speech-based interaction, accessible design, and personalized treatment tracking.

## Purpose

This application provides treatment apps to help users with:
- Short-term memory improvement
- Word finding exercises
- Cognitive function maintenance
- Memory training

**Target Audience**: Elderly users (65+) requiring:
- Large, readable fonts (18px base)
- High accessibility (WCAG AAA compliant)
- Simple, intuitive interfaces
- Speech-based interactions

## Architecture

- **Frontend**: Next.js 14+ (React, TypeScript, Tailwind CSS)
- **Backend**: FastAPI (Python 3.12+)
- **Database**: Supabase (PostgreSQL, Auth, Storage)
- **AI**: OpenAI GPT-4o-mini
- **Speech**: Google Cloud Speech-to-Text & Text-to-Speech
- **Email**: Resend
- **Hosting**: Google Cloud Run
- **Domain**: [words.parrotsoftware.com](https://words.parrotsoftware.com)

```
┌─────────────┐      ┌──────────────┐
│  Next.js    │─────→│   FastAPI    │
│  Frontend   │      │   Backend    │
└──────┬──────┘      └───────┬──────┘
       │                     │
       ├─────────────────────┼───→ Supabase (Auth, DB, Storage)
       │                     │
       └─────────────────────┼───→ Google Cloud Speech APIs
                             │
                             └───→ OpenAI GPT-4o-mini
```

## Quick Start

### Prerequisites

- Node.js 20+
- Python 3.12+
- uv (Python package manager)
- Git

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/fweiner/life-words.git
   cd life-words
   ```

2. **Set up Frontend**:
   ```bash
   cd frontend
   npm install
   cp .env.local.example .env.local
   # Edit .env.local with your API keys
   ```

3. **Set up Backend**:
   ```bash
   cd backend
   uv sync
   cp .env.local.example .env.local
   # Edit .env.local with your API keys
   ```

4. **Run Locally**:

   **Terminal 1** (Backend):
   ```bash
   cd backend
   uv run uvicorn app.main:app --reload
   # Runs on http://localhost:8000
   ```

   **Terminal 2** (Frontend):
   ```bash
   cd frontend
   npm run dev
   # Runs on http://localhost:3000
   ```

5. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Detailed Setup Guides

For detailed step-by-step instructions, see the setup guides in [`docs/setup/`](./docs/setup/):

1. [OpenAI API Setup](./docs/setup/01-openai-setup.md) - Create and configure OpenAI API keys
2. [Google Cloud Platform Setup](./docs/setup/02-gcp-setup.md) - Set up GCP project, Speech APIs, and service accounts
3. [Resend Email Setup](./docs/setup/03-resend-setup.md) - Configure email service and DNS
4. [GitHub Secrets Configuration](./docs/setup/04-github-secrets.md) - Set up CI/CD secrets
5. [Domain & Deployment](./docs/setup/05-domain-deployment.md) - Deploy to Cloud Run and configure DNS
6. [Supabase Database Setup](./docs/setup/06-supabase-setup.md) - Create database schema and configure authentication

## Environment Variables

### Frontend (`.env.local`)

```env
NEXT_PUBLIC_SUPABASE_URL=https://nnvqtxwobvyitqbsdskc.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-publishable-key
NEXT_PUBLIC_API_URL=http://localhost:8000
RESEND_API_KEY=your-resend-key
```

### Backend (`.env.local`)

```env
SUPABASE_URL=https://nnvqtxwobvyitqbsdskc.supabase.co
SUPABASE_SECRET_KEY=your-supabase-secret-key
OPENAI_API_KEY=your-openai-key
GOOGLE_CLOUD_PROJECT=life-words-production
GOOGLE_APPLICATION_CREDENTIALS=gcp-runtime.json
RESEND_API_KEY=your-resend-key
ALLOWED_ORIGINS=http://localhost:3000,https://words.parrotsoftware.com
```

## Project Structure

```
life-words/
├── frontend/               # Next.js application
│   ├── app/               # App router pages
│   │   ├── (auth)/       # Public auth pages
│   │   └── (dashboard)/  # Protected treatment pages
│   ├── components/        # React components
│   ├── lib/              # Utilities (Supabase, etc.)
│   └── middleware.ts     # Auth middleware
│
├── backend/               # FastAPI application
│   ├── app/
│   │   ├── main.py       # FastAPI entry point
│   │   ├── core/         # Database, auth, config
│   │   ├── routers/      # API endpoints
│   │   ├── services/     # Business logic
│   │   └── models/       # Pydantic schemas
│   └── pyproject.toml    # uv dependencies
│
├── docs/
│   ├── setup/            # Setup guides
│   └── claude.md         # Technical documentation
│
├── .github/workflows/    # CI/CD pipelines
└── .vscode/             # Debug configurations
```

## Development

### VSCode Debugging

Use the pre-configured debug configurations in `.vscode/launch.json`:

1. **Full Stack Debug** - Debug both frontend and backend simultaneously
2. **FastAPI Backend** - Debug backend only
3. **Next.js Frontend** - Debug frontend only

Press `F5` and select the configuration.

### Running Tests

```bash
# Frontend tests
cd frontend
npm run test

# Backend tests
cd backend
uv run pytest
```

## Deployment

### Automatic Deployment

Deployment is automated via GitHub Actions when you create a release:

1. Commit your changes to the `main` branch
2. Create a new release on GitHub with a version tag (e.g., `v1.0.1`)
3. GitHub Actions automatically builds and deploys to Google Cloud Run

### Manual Deployment

```bash
# Build and push Docker images
docker build --platform linux/amd64 -t us-docker.pkg.dev/life-words-production/gcr.io/treatment-web:latest ./frontend
docker build --platform linux/amd64 -t us-docker.pkg.dev/life-words-production/gcr.io/treatment-api:latest ./backend

docker push us-docker.pkg.dev/life-words-production/gcr.io/treatment-web:latest
docker push us-docker.pkg.dev/life-words-production/gcr.io/treatment-api:latest

# Deploy to Cloud Run (use gcloud CLI)
gcloud run deploy treatment-web \
  --image us-docker.pkg.dev/life-words-production/gcr.io/treatment-web:latest \
  --region us-central1 \
  --project life-words-production

gcloud run deploy treatment-api \
  --image us-docker.pkg.dev/life-words-production/gcr.io/treatment-api:latest \
  --region us-central1 \
  --project life-words-production
```

See [Domain & Deployment Guide](./docs/setup/05-domain-deployment.md) for detailed instructions.

## Database

### Schema Overview

- **profiles** - User profile information
- **treatment_sessions** - Individual treatment session records
- **treatment_results** - Session outcomes and scores
- **user_progress** - Aggregated progress statistics

### Database Migrations

Supabase migrations are managed via SQL scripts in the Supabase dashboard.

See [Supabase Setup Guide](./docs/setup/06-supabase-setup.md) for schema details and setup instructions.

## Treatment Apps

### Implemented

1. **Word Finding** - Image-based word recall with semantic cues
2. **Life Words** - Personal contacts and items naming practice

### Planned

3. Short Term Memory
4. Pattern Recognition
5. Sequential Memory
6. Visual Perception
7. Auditory Processing
8. Problem Solving
9. Attention Training
10. Executive Function

## Accessibility

This application is designed to meet WCAG AAA accessibility standards:

- **Large fonts**: 18px base size (vs standard 16px)
- **High contrast**: 7:1 ratio for normal text
- **Touch targets**: Minimum 44x44px
- **Keyboard navigation**: Full keyboard support
- **Screen reader compatible**: ARIA labels on all interactive elements
- **Reduced motion**: Respects user preferences
- **Semantic HTML**: Proper use of headings, landmarks, and roles

## Troubleshooting

### Common Issues

**CORS Errors**:
- Check `ALLOWED_ORIGINS` in backend `.env.local`
- Verify frontend `NEXT_PUBLIC_API_URL` is correct

**Authentication Errors**:
- Verify Supabase keys are correct
- Check user email is confirmed
- Ensure RLS policies allow the operation

**Speech API Errors**:
- Verify Google Cloud credentials are set up
- Check Speech APIs are enabled in GCP console
- Ensure service account has correct permissions

See [docs/claude.md](./docs/claude.md) for more troubleshooting tips.

## Documentation

- [Technical Documentation](./docs/claude.md) - Comprehensive technical guide
- [Setup Guides](./docs/setup/) - Step-by-step setup instructions
- [API Documentation](http://localhost:8000/docs) - FastAPI auto-generated docs (when running locally)

## License

This project is proprietary and confidential.

## Author

**Fred Weiner**
- Email: weiner@parrotsoftware.com
- GitHub: [@fweiner](https://github.com/fweiner)

## Acknowledgments

- Built with [Next.js](https://nextjs.org/)
- Backend powered by [FastAPI](https://fastapi.tiangolo.com/)
- Database and auth by [Supabase](https://supabase.com/)
- AI by [OpenAI](https://openai.com/)
- Speech by [Google Cloud](https://cloud.google.com/)
- Email by [Resend](https://resend.com/)
- UI components by [shadcn/ui](https://ui.shadcn.com/)
- Styling by [Tailwind CSS](https://tailwindcss.com/)
