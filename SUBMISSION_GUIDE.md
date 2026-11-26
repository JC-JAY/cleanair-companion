# 🏆 CleanAir Companion — Hackathon Submission Guide

This document contains everything needed to complete your hackathon submission.

---

## 📋 1. Form Fields — Copy & Paste

### Field 1: Public GitHub Repository Link
```text
https://github.com/JC-JAY/cleanair-companion
```
*(Verified: Public Access · Size: ~220 KiB, well under the 10 MB limit)*

---

### Field 2: Project Deployed Link
```text
https://cleanair-companion.vercel.app/dashboard
```
*(Verified: Live on Vercel · Status 200 OK · Responsive on Mobile & Desktop)*

---

### Field 3: Project Demo Video Submission
Upload your 90-second screen recording MP4 to Google Drive or YouTube and paste the link here:
```text
https://drive.google.com/file/d/YOUR_FILE_ID/view?usp=sharing
```
*(⚠️ Ensure Google Drive link sharing is set to **"Anyone with the link can view"**)*

---

### Field 4: Describe the changes/updates made in the deployed version
*(Length: 760 characters / 1024 limit)*

```text
Built CleanAir Companion, a full-stack GenAI PWA helping families navigate severe winter smog (Maharashtra/Pune focus, extensible to any city):
- Backend (FastAPI, Python 3.12, SQLAlchemy, Alembic, PostgreSQL + pgvector, Redis, Celery): Live AQI & meteorology (OpenAQ, Open-Meteo), JWT + anonymous auth, lifestyle profile, daily plan generator, RAG Q&A chat, community groups, and alert preferences.
- Deterministic Impact Calculator: Computes PM2.5 exposure reduction (µg/m³-h), CO2e/PM/NO2 avoided, and plain-language health meanings using cited IPCC, ARAI, WHO, Chafe et al., and BEE factors—LLMs never invent numbers.
- Frontend (Angular 18, Angular Material, PWA/ngsw): Onboarding wizard, AQI dashboard, daily plan, RAG chat with citations, settings, and EN/HI/MR i18n.
- Guardrails: Prompt-injection sanitizer, RAG refusal (<0.72 similarity), medical symptom escalation, and 2dp location rounding.
```

---

### Field 5: Mention the Gen AI services utilized in the submission, and where did you utilize it?
*(Length: 980 characters / 1024 limit)*

```text
1. Google Gemini API (Gemini 1.5 Pro & Flash):
   - Daily Plan Generator (backend/app/services/plan/): Utilized Gemini's Structured Outputs (JSON Schema & Function Calling) to generate personalized clean-air routines, optimal outdoor activity windows, and indoor hacks strictly grounded in deterministic health & emission calculations.
   - Grounded Chat Assistant (backend/app/services/chat/): Powered conversational Q&A using Gemini with strict safety settings, citation enforcement, and automatic medical escalation for acute respiratory symptoms.

2. Google Text Embedding API (text-embedding-004) + PostgreSQL pgvector:
   - Knowledge Base Ingestion & RAG (backend/app/services/rag/): Chunks and generates dense vector embeddings of WHO AQG 2021, CPCB AQI standards, and Maharashtra winter smog advisories into a pgvector HNSW index for high-precision semantic retrieval with grounded similarity thresholds (refusing ungrounded queries).
```

---

### Field 6: LinkedIn Post
Post the text in **Section 2** on your LinkedIn profile, then copy the post link and paste it here:
```text
https://www.linkedin.com/posts/YOUR_USERNAME_activity_xxxxxxxxx
```

---

## 📢 2. LinkedIn Post Content

Copy the text below and post it on LinkedIn (attach `screenshots/01_dashboard.png` for maximum reach):

```text
Severe winter smog and morning temperature inversions affect millions of families across urban India every winter. Most air quality apps only show a scary number—they don’t tell you what actions actually protect your family, or how much difference your choices make.

To solve this, I built 🍃 CleanAir Companion — a GenAI-powered assistant designed to help families and communities navigate severe air pollution with actionable, lifestyle-aware routines.

💡 What CleanAir Companion does:
1. 📊 Live Air Quality & Meteorology: Real-time AQI, PM2.5, PM10, NO₂, humidity, and winter temperature inversion detection via CPCB and Open-Meteo feeds.
2. 🗓️ "Today's Clean Air Plan": Uses Google Gemini 1.5 with structured JSON schemas to identify optimal outdoor activity windows (e.g., 12 PM–4 PM) and warn against dangerous morning inversion traps.
3. 📐 Deterministic Impact Calculator: No AI hallucinations. Every recommendation calculates exact PM2.5 exposure reduction (µg/m³·h) and CO₂e avoided using verified IPCC, ARAI, WHO, and BEE emission factors.
4. 🤖 Grounded RAG Assistant: Powered by Google text-embedding-004 and PostgreSQL pgvector to answer questions on masks, ventilation, and child health, backed by verified WHO & CPCB citations.
5. 🌍 Inclusive & Offline-Ready: PWA support, WCAG AA accessibility, and native multi-language support (English, हिन्दी, मराठी).

🛠️ Tech Stack:
- Frontend: Angular 18, Angular Material, Service Worker PWA
- Backend: Python 3.12, FastAPI, PostgreSQL + pgvector, Redis, Celery
- AI & Embeddings: Google Gemini 1.5 Flash/Pro, Google text-embedding-004

🔗 Try the Live App: https://cleanair-companion.vercel.app/dashboard
⭐ Public GitHub Repo: https://github.com/JC-JAY/cleanair-companion

Built with passion for the Google Developer Hackathon! Would love to hear your feedback in the comments. 

#GoogleDevelopers #GDG #GeminiSprint #GenAI #AirQuality #CleanAir #Sustainability #FastAPI #Angular #GoogleAI #BuildWithAI
```

---

## 🎬 3. Video Recording Script (90 Seconds)

Match this spoken script to the 6 screenshots in your `screenshots/` directory:

| Time | Slide / Screen | Spoken Script |
|---|---|---|
| **0:00 – 0:15** | `02_onboarding.png` | *"Hello judges! Welcome to CleanAir Companion — an AI-powered assistant designed for families navigating severe winter smog and urban air pollution, starting with Maharashtra's Pune region. It starts with a 4-step onboarding wizard capturing your location, household vulnerability like asthma and children, commute mode, and available devices to personalize every recommendation."* |
| **0:15 – 0:30** | `01_dashboard.png` | *"On the live Dashboard, users get real-time air quality metrics via Open-Meteo and CPCB feeds. Notice our dynamic CPCB spectrum bar with a real-time pointer, pollutant KPI tiles for PM2.5, PM10, and NO₂, and an automated winter temperature inversion alert that warns families when surface-level cold air is trapping smoke and particulate matter."* |
| **0:30 – 0:48** | `03_daily_plan.png` | *"Here is Today's Clean Air Plan, generated using Google Gemini 1.5 with structured JSON schemas. It identifies optimal outdoor windows — recommending outdoor activity between 12:00 and 4:00 PM while warning against peak morning inversion. Crucially, our deterministic Python Impact Calculator computes exact PM2.5 inhalation saved and CO2e avoided using cited IPCC and ARAI factors — meaning the AI explains real numbers and never hallucinates statistics."* |
| **0:48 – 1:05** | `04_ai_assistant.png` | *"Our conversational assistant uses Retrieval-Augmented Generation powered by Google text-embedding-004 and pgvector. It answers questions about N95 masks, DIY purifiers, and child respiratory safety. Every response includes verified citations from WHO and CPCB guidelines, with built-in prompt-injection protection and automatic medical escalation for acute symptoms."* |
| **1:05 – 1:18** | `05_community.png` | *"Clean air is a collective effort. Community mode enables neighborhood and school groups in Pune to join weekly low-emission challenges, tracking collective emissions avoided and particulate exposure saved across the community."* |
| **1:18 – 1:30** | `06_settings.png` | *"Designed for accessibility, CleanAir Companion supports English, Hindi, and Marathi, large-text mode, and offline PWA caching for low-bandwidth networks. Built with Google Gemini, FastAPI, and Angular 18. Thank you!"* |
