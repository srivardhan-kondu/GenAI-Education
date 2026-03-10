<div align="center">

# 🎓 EduGen AI

### Educational Content Auto-Generation System Using Generative AI

An AI-powered platform that automatically generates **multimodal learning modules** — including structured text, AI-generated images, animated concept videos, voice narration, and downloadable study notes — from any topic, using entirely free-tier Generative AI APIs.

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)](https://react.dev)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248?logo=mongodb&logoColor=white)](https://www.mongodb.com/atlas)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## 📑 Table of Contents

1. [Features](#-features)
2. [Tech Stack](#-tech-stack)
3. [Architecture & Flow](#-architecture--flow)
4. [Project Structure](#-project-structure)
5. [Prerequisites](#-prerequisites)
6. [API Keys — Setup Guide](#-api-keys--setup-guide)
7. [Installation & Setup](#-installation--setup)
8. [Running the Project](#-running-the-project)
9. [Usage Guide](#-usage-guide)
10. [API Endpoints Reference](#-api-endpoints-reference)
11. [Environment Variables Reference](#-environment-variables-reference)
12. [Troubleshooting](#-troubleshooting)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📖 **Structured Text Content** | AI-generated definitions, explanations, examples, key points, and summaries — tailored to difficulty level |
| 🖼 **AI-Generated Images** | Concept diagrams and educational infographics generated via FLUX.1-schnell (HuggingFace) |
| 🎬 **Animated Concept Videos** | Real MP4 slideshow videos with zoom/pan effects, text overlays, and transitions — built locally from AI images |
| 🔊 **Voice Narration** | AI-narrated audio summaries using ElevenLabs text-to-speech |
| 📝 **Smart Study Notes** | Three formats: Structured Notes, Cornell Notes (AI-generated), and Flashcards (AI-generated) |
| 📄 **PDF Export** | Download notes as professionally formatted PDFs |
| 🔐 **User Authentication** | JWT-based registration, login, and profile management |
| 📚 **Module History** | Browse and revisit all previously generated learning modules |
| 🔍 **Search** | Full-text search across your generated modules |
| 🎯 **Difficulty Levels** | Beginner, Intermediate, and Advanced content personalization |
| ⚡ **Concurrent Generation** | Images, video, and audio are generated in parallel for speed |

---

## 🛠 Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React 18 + Vite + Tailwind CSS | Single-page app with responsive UI |
| **Backend** | Python 3.11 + FastAPI | Async REST API server |
| **Database** | MongoDB (Motor async driver) | User data and module storage |
| **Text AI** | OpenAI GPT-4o-mini | Educational content and notes generation |
| **Image AI** | FLUX.1-schnell (HuggingFace) | Concept diagrams and infographics |
| **Video** | moviepy + Pillow (local) | Animated MP4 videos from AI images |
| **Voice AI** | ElevenLabs TTS | Audio narration |
| **Auth** | JWT (python-jose) + bcrypt | Secure token-based authentication |
| **PDF** | fpdf2 | Study notes export |

---

## 🏗 Architecture & Flow

### High-Level System Architecture

```
┌──────────────────┐         HTTP/JSON         ┌──────────────────────┐
│                  │ ◄──────────────────────►   │                      │
│   React Frontend │        Port 5173           │   FastAPI Backend     │
│   (Vite + TW)    │                            │   Port 8000          │
│                  │                            │                      │
└──────────────────┘                            └──────┬───────────────┘
                                                       │
                       ┌───────────────────────────────┼───────────────────────┐
                       │                               │                       │
                ┌──────▼──────┐               ┌───────▼───────┐        ┌──────▼──────┐
                │  MongoDB    │               │  External AI  │        │   Local     │
                │  Atlas /    │               │  APIs         │        │  Processing │
                │  Local      │               │               │        │             │
                │  ─ users    │               │  • OpenAI     │        │  • moviepy  │
                │  ─ modules  │               │  • HuggingFace│        │  • Pillow   │
                └─────────────┘               │  • ElevenLabs │        │  • fpdf2    │
                                              └───────────────┘        └─────────────┘
```

### Content Generation Pipeline (What happens when you click "Generate")

```
Step 1 ─► Text Generation (OpenAI GPT-4o-mini)
          │  Produces: definition, explanation, examples, key_points, summary, concepts
          │
Step 2 ─► Run in PARALLEL:
          │
          ├─► Image Generation (HuggingFace FLUX.1-schnell)
          │   • Sends concept prompts → receives JPEG images
          │   • Up to 3 concepts, generated concurrently
          │
          ├─► Video Generation (FLUX + moviepy)
          │   • Generates concept images via FLUX
          │   • Builds animated MP4 with title slide, zoom effects, labels
          │   • Up to 3 concepts combined into one video
          │
          └─► Voice Narration (ElevenLabs TTS)
              • Builds narration script from definition + key points + summary
              • Sends to ElevenLabs → receives MP3 audio
              │
Step 3 ─► Assembly
          │  Combines all outputs into a LearningModule object
          │
Step 4 ─► Persistence
          │  Saves to MongoDB → Returns full module to frontend
          │
Step 5 ─► Frontend Display
             Renders text, images, video player, audio player, and notes tabs
```

### User Flow

```
Register/Login → Dashboard → Enter Topic → Configure Options → Generate
                                                                    │
                                              ┌─────────────────────┘
                                              ▼
                                    Learning Module Page
                                    ├── 📖 Content Tab  (text)
                                    ├── 🖼 Images Tab   (diagrams)
                                    ├── 🎬 Video Tab    (animated MP4)
                                    ├── 🔊 Audio Tab    (narration)
                                    └── 📝 Notes Tab    (structured / cornell / flashcards + PDF)
```

---

## 📂 Project Structure

```
edugen-ai/
│
├── README.md                         ← You are here
├── progress.md                       ← Feature tracker & progress log
│
├── backend/                          ← Python FastAPI server
│   ├── .env                          ← API keys & config (create from .env.example)
│   ├── .env.example                  ← Template for environment variables
│   ├── requirements.txt              ← Python dependencies
│   ├── app/
│   │   ├── main.py                   ← FastAPI app entry point, CORS, routers
│   │   ├── config.py                 ← Pydantic settings (reads .env)
│   │   │
│   │   ├── database/
│   │   │   └── connection.py         ← MongoDB async connection (Motor)
│   │   │
│   │   ├── models/
│   │   │   ├── user.py               ← User Pydantic schemas
│   │   │   └── content.py            ← ContentRequest, LearningModule, ImageData, VideoData
│   │   │
│   │   ├── routes/
│   │   │   ├── auth.py               ← Register, Login, Profile endpoints
│   │   │   ├── content.py            ← Generate module, History, Get module
│   │   │   ├── notes.py              ← Generate notes (JSON + PDF export)
│   │   │   └── search.py             ← Search across modules
│   │   │
│   │   ├── services/
│   │   │   ├── text_generation.py    ← OpenAI GPT-4o-mini text content
│   │   │   ├── image_generation.py   ← HuggingFace FLUX.1-schnell images
│   │   │   ├── video_generation.py   ← FLUX images → animated MP4 (moviepy)
│   │   │   ├── voice_generation.py   ← ElevenLabs text-to-speech
│   │   │   ├── notes_generation.py   ← Structured/Cornell/Flashcard notes
│   │   │   ├── pdf_export.py         ← PDF rendering with fpdf2
│   │   │   └── content_integration.py ← Orchestration layer (ties everything together)
│   │   │
│   │   └── utils/
│   │       ├── auth_utils.py         ← JWT creation, password hashing, token verification
│   │       └── validators.py         ← Input sanitization & validation
│   │
│   └── venv/                         ← Python virtual environment (git-ignored)
│
└── frontend/                         ← React single-page application
    ├── index.html                    ← HTML entry point
    ├── package.json                  ← Node.js dependencies
    ├── vite.config.js                ← Vite dev server config (port 5173)
    ├── tailwind.config.js            ← Tailwind CSS configuration
    ├── postcss.config.js             ← PostCSS plugins
    └── src/
        ├── main.jsx                  ← React DOM entry point
        ├── App.jsx                   ← Routes & layout
        ├── index.css                 ← Global styles + Tailwind directives
        ├── context/
        │   └── AuthContext.jsx       ← Authentication state management
        ├── services/
        │   └── api.js                ← Axios API client with JWT interceptor
        └── components/
            ├── ProtectedRoute.jsx    ← Auth guard for routes
            ├── Auth/
            │   ├── Login.jsx         ← Login page
            │   └── Register.jsx      ← Registration page
            ├── Navbar/
            │   └── Navbar.jsx        ← Navigation bar
            ├── Dashboard/
            │   └── Dashboard.jsx     ← Home dashboard
            ├── TopicInput/
            │   └── TopicInput.jsx    ← Module generation form with options
            ├── LearningModule/
            │   ├── LearningModule.jsx ← Module viewer with tabs
            │   ├── TextContent.jsx   ← Text content renderer
            │   ├── ImageContent.jsx  ← Image gallery with lightbox
            │   ├── VideoContent.jsx  ← MP4 video player
            │   ├── AudioContent.jsx  ← Audio player with download
            │   └── NotesPanel.jsx    ← Notes viewer (3 formats + PDF)
            ├── History/
            │   └── History.jsx       ← Past modules list
            ├── Search/
            │   └── Search.jsx        ← Module search page
            └── Profile/
                └── Profile.jsx       ← User profile & preferences
```

---

## 📋 Prerequisites

Before setting up the project, make sure you have the following installed on your system:

| Tool | Version | Installation |
|------|---------|-------------|
| **Python** | 3.11 or higher | [python.org/downloads](https://www.python.org/downloads/) |
| **Node.js** | 18 or higher | [nodejs.org](https://nodejs.org/) |
| **npm** | 9+ (comes with Node.js) | Included with Node.js |
| **Git** | Any recent version | [git-scm.com](https://git-scm.com/) |
| **MongoDB** | Atlas (cloud) or local | See [Database Setup](#step-2-database-setup) below |

### Verify installations

```bash
python3 --version    # Should show 3.11+
node --version       # Should show v18+
npm --version        # Should show 9+
git --version        # Any version
```

---

## 🔑 API Keys — Setup Guide

This project uses **4 free-tier API keys**. Here's exactly how to get each one and what it does:

### 1. OpenAI API Key — `OPENAI_API_KEY`

> **Purpose:** Powers all text content generation (educational text, Cornell notes, flashcards) using GPT-4o-mini.

**How to get it:**
1. Go to [platform.openai.com](https://platform.openai.com/)
2. Sign up or log in to your account
3. Navigate to **API Keys** → [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
4. Click **"Create new secret key"**
5. Give it a name (e.g., `edugen-ai`) and click **Create**
6. **Copy the key immediately** — it starts with `sk-proj-...`
7. Paste it into your `.env` file as `OPENAI_API_KEY`

> ⚠️ **Note:** OpenAI offers a free trial with $5 credit. After that, it's pay-as-you-go. GPT-4o-mini is very affordable (~$0.15 per 1M input tokens).

---

### 2. HuggingFace API Key — `HUGGINGFACE_API_KEY`

> **Purpose:** Generates AI images (concept diagrams, infographics) using the FLUX.1-schnell model. Also used to create base images for animated videos.

**How to get it:**
1. Go to [huggingface.co](https://huggingface.co/) and create a free account
2. Click your **profile icon** (top right) → **Settings**
3. Go to **Access Tokens** → [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
4. Click **"Create new token"**
5. Name it (e.g., `edugen-ai`), select **"Read"** permission, click **Generate**
6. Copy the token — it starts with `hf_...`
7. Paste it into your `.env` file as `HUGGINGFACE_API_KEY`

> ✅ **100% free.** The FLUX.1-schnell model is free on HuggingFace's Inference API with rate limits.

---

### 3. ElevenLabs API Key — `ELEVENLABS_API_KEY`

> **Purpose:** Converts text to natural-sounding voice narration (text-to-speech). Generates MP3 audio summaries of each module.

**How to get it:**
1. Go to [elevenlabs.io](https://elevenlabs.io/) and sign up for a **free account**
2. After logging in, click your **profile icon** (bottom left) → **Profile + API key**
3. Or go directly to [elevenlabs.io/app/settings/api-keys](https://elevenlabs.io/app/settings/api-keys)
4. Your API key is displayed — click the **eye icon** to reveal it, then **copy**
5. Paste it into your `.env` file as `ELEVENLABS_API_KEY`

> ✅ **Free tier:** 10,000 characters/month. Each module narration uses ~500-1500 characters, so you can generate ~7-20 modules/month for free.

**Voice ID (optional):**  
The default voice is **Rachel** (`21m00Tcm4TlvDq8ikWAM`). To use a different voice:
1. Go to [elevenlabs.io/app/voice-library](https://elevenlabs.io/app/voice-library)
2. Find a voice you like → click on it → copy its **Voice ID**
3. Set `ELEVENLABS_VOICE_ID` in your `.env`

---

### 4. MongoDB — `MONGODB_URL`

> **Purpose:** Stores all user accounts, learning modules, and their generated content.

**Option A: MongoDB Atlas (Cloud — Recommended)**
1. Go to [mongodb.com/atlas](https://www.mongodb.com/atlas) and create a free account
2. Create a **free shared cluster** (M0 tier — always free)
3. Under **Database Access** → Add a database user with a username and password
4. Under **Network Access** → Add your IP address (or `0.0.0.0/0` for development)
5. On the cluster page, click **Connect** → **Connect your application** → **Driver: Python**
6. Copy the connection string — it looks like:
   ```
   mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/
   ```
7. Replace `<username>` and `<password>` with your database user credentials
8. Paste into your `.env` as `MONGODB_URL`

**Option B: Local MongoDB**
```bash
# Using Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Then in your .env:
MONGODB_URL=mongodb://localhost:27017
```

---

### API Key Summary

| Key | Service | What It Does | Cost |
|-----|---------|-------------|------|
| `OPENAI_API_KEY` | OpenAI GPT-4o-mini | Text content, Cornell notes, flashcards | Free trial ($5 credit), then ~$0.15/1M tokens |
| `HUGGINGFACE_API_KEY` | HuggingFace FLUX.1 | Concept images & video base frames | **Free** (rate-limited) |
| `ELEVENLABS_API_KEY` | ElevenLabs TTS | Voice narration (MP3 audio) | **Free** (10K chars/month) |
| `MONGODB_URL` | MongoDB Atlas | User & module database | **Free** (M0 cluster) |

---

## 🚀 Installation & Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/edugen-ai.git
cd edugen-ai
```

> Replace `your-username/edugen-ai` with your actual repository URL.

---

### Step 2: Database Setup

Choose **one** option:

**Option A — MongoDB Atlas (Cloud)**
Follow the steps in the [MongoDB section](#4-mongodb--mongodb_url) above to get your connection string.

**Option B — Local MongoDB (Docker)**
```bash
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

---

### Step 3: Backend Setup

```bash
# Navigate to the backend directory
cd backend

# Create a Python virtual environment
python3 -m venv venv

# Activate the virtual environment
# macOS / Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

#### Create the `.env` file

```bash
# Copy the example file
cp .env.example .env
```

Now open `backend/.env` in your editor and fill in your API keys:

```env
# Security — change this to any random 32+ character string
SECRET_KEY=your-random-secret-key-at-least-32-chars

# MongoDB connection
MONGODB_URL=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/
DATABASE_NAME=edugen_db

# OpenAI — for text generation and notes
OPENAI_API_KEY=sk-proj-your-key-here

# HuggingFace — for image generation
HUGGINGFACE_API_KEY=hf_your-key-here

# ElevenLabs — for voice narration
ELEVENLABS_API_KEY=sk_your-key-here
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
```

> ⚠️ **Important:** Never commit your `.env` file to Git. It's already in `.gitignore`.

---

### Step 4: Frontend Setup

```bash
# Open a new terminal, navigate to the frontend directory
cd frontend

# Install Node.js dependencies
npm install
```

No additional configuration is needed for the frontend — it's pre-configured to connect to `http://localhost:8000`.

---

## ▶️ Running the Project

You need **two terminal windows** — one for the backend and one for the frontend.

### Terminal 1: Start the Backend Server

```bash
cd backend
source venv/bin/activate      # macOS/Linux
# venv\Scripts\activate       # Windows

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
✅ MongoDB connected successfully.
```

> The `--reload` flag auto-restarts the server when you change any Python file.

**Verify the backend is running:**
- Health check: [http://localhost:8000/health](http://localhost:8000/health)
- API docs (Swagger UI): [http://localhost:8000/docs](http://localhost:8000/docs)
- API docs (ReDoc): [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Terminal 2: Start the Frontend Dev Server

```bash
cd frontend
npm run dev
```

You should see:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
```

### Open the App

Open your browser and go to: **[http://localhost:5173](http://localhost:5173)**

---

## 📖 Usage Guide

### 1. Create an Account
- Open **http://localhost:5173** → click **Register**
- Enter your name, email, and password → Submit
- You'll be automatically logged in and redirected to the Dashboard

### 2. Generate a Learning Module
- Click **"Generate"** in the navbar (or the button on the Dashboard)
- **Enter a topic** (e.g., "Binary Search", "Photosynthesis", "Neural Networks")
- **Choose difficulty:** Beginner / Intermediate / Advanced
- **Choose style:** Detailed or Short
- **Toggle media options:**
  - 🖼 **Images** — ON by default (AI concept diagrams)
  - 🔊 **Audio** — ON by default (voice narration)
  - 🎬 **Video** — OFF by default (animated MP4 — enable this toggle!)
- Click **Generate** — wait ~30-60 seconds while the AI creates your module

### 3. Explore the Module
Once generated, you'll see **tabs** at the top:

| Tab | Content |
|-----|---------|
| 📖 **Content** | Full text: definition, explanation, examples, key points, summary |
| 🖼 **Images** | AI-generated concept diagrams (click to enlarge) |
| 🎬 **Video** | Animated MP4 video with playback controls + download |
| 🔊 **Audio** | Audio narration with play/pause + MP3 download |
| 📝 **Notes** | Study notes in 3 formats + PDF download |

### 4. Study Notes
In the **Notes** tab, choose a format:
- **Structured Notes** — organized text sections (no additional AI call)
- **Cornell Notes** — AI-generates cue/notes pairs + summary (classic study method)
- **Flashcards** — AI-generates Q&A pairs for self-testing

Each format can be **downloaded as a PDF**.

### 5. History & Search
- **History** page — browse all previously generated modules
- **Search** page — search modules by topic keyword

---

## 📡 API Endpoints Reference

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/register` | Create a new account |
| `POST` | `/auth/login` | Log in and receive JWT token |
| `GET` | `/auth/me` | Get current user profile (requires token) |
| `PUT` | `/auth/profile` | Update user name/preferences (requires token) |

### Content Generation
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/content/generate` | Generate a full learning module |
| `GET` | `/content/history` | Get user's module history |
| `GET` | `/content/{module_id}` | Get a specific module by ID |

### Notes
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/notes/{module_id}?format=structured` | Generate notes (JSON) |
| `GET` | `/notes/{module_id}/pdf?format=cornell` | Download notes as PDF |

> Supported formats: `structured`, `cornell`, `flashcards`

### Search
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/search/?q=keyword` | Search modules by topic |

### System
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/docs` | Swagger UI (interactive API docs) |

---

## ⚙️ Environment Variables Reference

All variables are configured in `backend/.env`:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | Yes | — | JWT signing secret (32+ random characters) |
| `MONGODB_URL` | Yes | `mongodb://localhost:27017` | MongoDB connection string |
| `DATABASE_NAME` | No | `edugen_db` | MongoDB database name |
| `OPENAI_API_KEY` | Yes | — | OpenAI API key for text generation |
| `HUGGINGFACE_API_KEY` | Yes | — | HuggingFace token for image generation |
| `ELEVENLABS_API_KEY` | Yes | — | ElevenLabs API key for voice |
| `ELEVENLABS_VOICE_ID` | No | `21m00Tcm4TlvDq8ikWAM` | ElevenLabs voice (Rachel) |

---

## 🔧 Troubleshooting

### Backend won't start
```
ModuleNotFoundError: No module named 'app'
```
→ Make sure you're running `uvicorn` from **inside** the `backend/` directory.

### MongoDB connection failed
```
⚠️ MongoDB connection failed: ...
```
→ Check your `MONGODB_URL` in `.env`. For Atlas, ensure your IP is whitelisted under **Network Access**.

### Images not generating
```
Image generation failed [401]: ...
```
→ Your `HUGGINGFACE_API_KEY` may be invalid or expired. Generate a new token at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens).

### Voice narration not generating
```
Voice generation failed [401]: ...
```
→ Check your `ELEVENLABS_API_KEY`. If you see "subscription_required", you may have exhausted the free tier's monthly 10K character limit — it resets on the 1st of each month.

### Video tab not appearing
→ Video generation is **OFF by default**. Make sure to enable the **🎬 Video toggle** on the generation form before clicking Generate.

### Text generation failed
```
OpenAI API error 401: Incorrect API key
```
→ Your `OPENAI_API_KEY` is invalid. Go to [platform.openai.com/api-keys](https://platform.openai.com/api-keys) and create a new key.

### Frontend can't connect to backend
```
Network Error / CORS error
```
→ Make sure the backend is running on port **8000**. The frontend is configured to connect to `http://localhost:8000`.

### Port already in use
```bash
# Find and kill the process using port 8000
lsof -i :8000
kill -9 <PID>

# Or for port 5173
lsof -i :5173
kill -9 <PID>
```

---

## 📄 Quick Start (TL;DR)

```bash
# 1. Clone
git clone https://github.com/your-username/edugen-ai.git && cd edugen-ai

# 2. Backend
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env           # ← Fill in your API keys
uvicorn app.main:app --reload --port 8000

# 3. Frontend (new terminal)
cd frontend
npm install
npm run dev

# 4. Open http://localhost:5173
```

---

<div align="center">

**Built with ❤️ using Generative AI**

OpenAI • HuggingFace • ElevenLabs • FastAPI • React • MongoDB

</div>
