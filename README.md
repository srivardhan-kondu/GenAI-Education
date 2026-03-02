# EduGen AI — Educational Content Auto-Generation System

An AI-powered platform that automatically generates **multimodal learning modules** (text, images, voice) from any topic using Generative AI.

## Features
- Structured text explanations (Gemini AI)
- AI-generated visual diagrams (Stable Diffusion via HuggingFace)
- Voice narration (ElevenLabs TTS)
- User authentication (JWT)
- Module history and search
- Difficulty-level personalization (Beginner / Intermediate / Advanced)

## Tech Stack
| Layer | Technology |
|-------|-----------|
| Frontend | React 18 + Vite + Tailwind CSS |
| Backend | Python 3.11 + FastAPI |
| Database | MongoDB (Motor async) |
| Text AI | Google Gemini 1.5 Flash |
| Image AI | Stable Diffusion via HuggingFace Inference API |
| Voice AI | ElevenLabs TTS (free tier) |

## Project Structure
```
.
├── progress.md          ← Feature tracker & progress log
├── README.md
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database/connection.py
│   │   ├── models/          (user.py, content.py)
│   │   ├── routes/          (auth.py, content.py, search.py)
│   │   ├── services/        (text_generation.py, image_generation.py, voice_generation.py, content_integration.py)
│   │   └── utils/           (auth_utils.py, validators.py)
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── index.html
    ├── vite.config.js
    ├── tailwind.config.js
    ├── package.json
    └── src/
        ├── App.jsx
        ├── context/AuthContext.jsx
        ├── services/api.js
        └── components/
            ├── Auth/         (Login, Register)
            ├── Navbar/
            ├── Dashboard/
            ├── TopicInput/
            ├── LearningModule/  (TextContent, ImageContent, AudioContent)
            ├── History/
            └── Search/
```

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- MongoDB (local or Docker)
- API keys: Gemini, HuggingFace, ElevenLabs

### API Keys (Free Tiers)
| Service | Where to get |
|---------|-------------|
| Gemini API | https://aistudio.google.com/app/apikey |
| HuggingFace | https://huggingface.co/settings/tokens |
| ElevenLabs | https://elevenlabs.io (free tier → 10k chars/month) |

### 1. MongoDB
```bash
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

### 2. Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate        # macOS/Linux
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
uvicorn app.main:app --reload --port 8000
```
API docs available at: http://localhost:8000/docs

### 3. Frontend
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```
App available at: http://localhost:5173

## Environment Variables

### `backend/.env`
```env
SECRET_KEY=change-this-to-a-random-32-char-string
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=edugen_db
GEMINI_API_KEY=your_gemini_api_key
HUGGINGFACE_API_KEY=your_hf_token
ELEVENLABS_API_KEY=your_elevenlabs_key
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
```

### `frontend/.env`
```env
VITE_API_URL=http://localhost:8000
```

## API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login |
| GET | `/auth/me` | Current user info |
| PUT | `/auth/profile` | Update preferences |
| POST | `/content/generate` | Generate learning module |
| GET | `/content/history` | Module history |
| GET | `/content/{id}` | Get specific module |
| GET | `/search/?q=query` | Search modules |
| GET | `/health` | Health check |

## How It Works
1. User enters a topic + selects difficulty
2. Gemini generates structured educational content (JSON)
3. Key concepts are extracted from the content
4. HuggingFace generates images for each concept (concurrently)
5. ElevenLabs converts key text to audio narration (concurrently)
6. All media is assembled into a Learning Module and saved to MongoDB
7. User views/reads/listens on the React frontend

## Functional Requirements Coverage
- FR-1 through FR-8, FR-10 through FR-15: ✅ Implemented
- FR-9 (Video generation): Planned for future sprint

See [progress.md](./progress.md) for full task tracking.
