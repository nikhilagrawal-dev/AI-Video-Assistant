# 🎬 AI Video Assistant

> An AI-powered meeting and video intelligence assistant that transforms videos and audio into searchable, structured, and actionable insights.

[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-red?logo=streamlit)](https://streamlit.io/)
[![Whisper](https://img.shields.io/badge/Speech--to--Text-Whisper-green)](https://github.com/openai/whisper)
[![LangChain](https://img.shields.io/badge/LangChain-RAG-blue)](https://www.langchain.com/)
[![ChromaDB](https://img.shields.io/badge/Vector%20DB-Chroma-orange)](https://www.trychroma.com/)

---

## 📌 Overview

**AI Video Assistant** is an intelligent video and meeting analysis application built with Python and Streamlit.

The application takes a YouTube URL or an uploaded audio/video file and processes it through an AI pipeline to generate:

- 🎙️ Transcriptions
- 🏷️ Professional meeting titles
- 📝 Meeting summaries
- ✅ Action items
- 🔑 Key decisions
- ❓ Open questions
- 🧠 Context-aware RAG-based question answering

The application supports both **English** and **Hinglish** workflows. For English transcription, it uses **OpenAI Whisper** locally. For Hinglish speech, it uses **Sarvam AI's** speech-to-text translation API to produce an English transcript.

The generated transcript is converted into vector embeddings and stored in **ChromaDB**, enabling users to chat with their meeting transcript through a retrieval-augmented generation (RAG) pipeline.

---

## ✨ Features

### 🎥 Multiple Input Sources

The application supports:

- YouTube URLs
- MP4, WEBM, MOV
- WAV, MP3, M4A

Users can choose between:

```text
YouTube URL
      or
Upload File
```

### 🎙️ Intelligent Transcription

**English**
Transcribed locally using **OpenAI Whisper**, avoiding the need to send English audio to an external API.

**Hinglish**
Processed using **Sarvam AI** — speech is transcribed and translated into English for downstream analysis. Audio is split into short (~25-second) pieces before being sent to the API, in line with its synchronous duration limits.

### 🔊 Robust Audio Processing

Uploaded media is standardized via **FFmpeg** into:

- WAV
- PCM S16LE
- 16 kHz
- Mono

This ensures a consistent format across the transcription pipeline. Empty transcripts (silent or speechless files) are validated and filtered out before reaching the vector database stage.

### 📝 AI Meeting Summary

A professional meeting summary is generated after transcription, with Markdown support for:

- Headings
- Bold text
- Bullet points
- Structured sections

### ✅ Action Items

Actionable tasks are automatically extracted from the transcript, each including:

- Task description
- Owner
- Deadline

**Example:**

```text
1. Prepare the project report
   Owner: Rahul
   Deadline: Friday
```

### 🔑 Key Decisions

Important decisions made during the meeting are automatically extracted and displayed separately.

### ❓ Open Questions

The application identifies unresolved questions and topics requiring follow-up.

### 🧠 RAG-Powered Meeting Chat

The transcript is chunked and converted into embeddings, stored in **ChromaDB**. A retrieval-augmented generation pipeline then answers user questions based solely on the meeting transcript.

**Example:**

```text
User: What were the main decisions made?
AI:   The team decided to...
```

If the requested information isn't present in the transcript, the assistant says so rather than inventing an answer.

---

## 🏗️ System Architecture

```text
                    ┌─────────────────────┐
                    │      User Input      │
                    └──────────┬──────────┘
                               │
                 ┌─────────────┴─────────────┐
                 │                           │
          YouTube URL                   Upload File
                 │                           │
              yt-dlp                  MP4 / WEBM / MOV
                 │                    WAV / MP3 / M4A
                 │                           │
                 └─────────────┬─────────────┘
                               │
                               ▼
                         ┌───────────┐
                         │  FFmpeg   │
                         │  Audio    │
                         │ Conversion│
                         └─────┬─────┘
                               │
                               ▼
                       16kHz Mono WAV
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Audio Chunking     │
                    │    10 min chunks     │
                    └──────────┬──────────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
                 English               Hinglish
                    │                     │
                    ▼                     ▼
                Whisper               Sarvam AI
                    │                     │
                    │              25-second pieces
                    │                     │
                    └──────────┬──────────┘
                               │
                               ▼
                         Transcript
                               │
                ┌──────────────┼──────────────┐
                │              │              │
                ▼              ▼              ▼
             Summary       Extraction       Title
                │              │
                │       ┌──────┼──────┐
                │       │      │      │
                │    Actions Decisions Questions
                │
                └──────────────┬──────────────┘
                               │
                               ▼
                       Text Chunking
                               │
                               ▼
                       HuggingFace
                       Embeddings
                               │
                               ▼
                         ChromaDB
                               │
                               ▼
                        RAG Retriever
                               │
                               ▼
                        Mistral LLM
                               │
                               ▼
                        Chat Answer
```

---

## 🧰 Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Streamlit | Frontend and application UI |
| OpenAI Whisper | English speech transcription |
| Sarvam AI | Hinglish speech transcription/translation |
| FFmpeg | Audio/video processing |
| yt-dlp | YouTube media extraction |
| Deno | JavaScript runtime for yt-dlp |
| Mistral AI | Summarization, extraction, and RAG responses |
| LangChain | LLM and RAG orchestration |
| ChromaDB | Vector database |
| HuggingFace Embeddings | Transcript embeddings |
| PyDub | Audio chunking |
| python-dotenv | Environment configuration |

---

## 📂 Project Structure

```text
AI-Video-Assistant/
│
├── core/
│   ├── extractor.py
│   ├── rag_engine.py
│   ├── summarizer.py
│   ├── transcriber.py
│   └── vector_store.py
│
├── utils/
│   └── audio_processor.py
│
├── app.py
├── main.py
├── requirements.txt
├── packages.txt
├── .gitignore
└── README.md
```

---

## 🔄 Processing Pipeline

### 1. Input

The user provides either:

- A YouTube URL, **or**
- A local audio/video file

### 2. Audio Extraction

Video/audio is converted into a standardized format — 16 kHz, mono, PCM WAV — using FFmpeg for reliable media conversion.

### 3. Chunking

Long audio is divided into manageable chunks:

```text
Input Audio → 10-minute chunks → Transcription
```

For Hinglish/Sarvam processing, each chunk is further divided into 25-second pieces before being sent to Sarvam AI.

### 4. Transcription

```text
English   → Whisper
Hinglish  → Sarvam AI → English Transcript
```

### 5. AI Analysis

The transcript is processed to generate:

- Professional title
- Meeting summary
- Action items
- Key decisions
- Open questions

### 6. Vector Database

```text
Transcript → Text Splitter → HuggingFace Embeddings → ChromaDB
```

### 7. RAG Chat

```text
Question → Retriever → Relevant Transcript Chunks → Mistral AI → Context-Aware Answer
```

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/nikhilagrawal-dev/AI-Video-Assistant.git
cd AI-Video-Assistant
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
```

Activate it:

**macOS / Linux**
```bash
source .venv/bin/activate
```

**Windows**
```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

FFmpeg is also required.

For macOS:

```bash
brew install ffmpeg
```

---

## 🔐 Environment Variables

Create a `.env` file in the project root:

```env
MISTRAL_API_KEY=your_mistral_api_key
SARVAM_API_KEY=your_sarvam_api_key
```

Optional Whisper configuration:

```env
WHISPER_MODEL=small
SARVAM_STT_MODEL=saaras:v2.5
```

> ⚠️ **Important:** Never commit `.env` or API keys to GitHub.

---

## ▶️ Run the Application

Start the Streamlit app:

```bash
streamlit run app.py
```

The application will open at:

```
http://localhost:8501
```

---
