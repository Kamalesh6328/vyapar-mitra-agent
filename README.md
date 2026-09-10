# 🌟 Vyapar Mitra (व्यापार मित्र)
### AI Agent for Street Vendor Digitalization & Financial Inclusion
**Problem Statement No. 29: Street Vendor Digitalization Agent**

---

## 📌 Executive Summary
**Vyapar Mitra** is a production-ready, multimodal, multilingual AI agent tailored specifically for informal micro-entrepreneurs and street vendors across India. It addresses the critical digital divide by empowering vendors with voice-first micro-accounting, automated government credit facilitation (**PM SVANidhi**), open commerce onboarding (**ONDC**), hyperlocal Mandi pricing intelligence, and instant marketing asset generation in regional Indian languages (**मराठी (Marathi)**, **हिंदी (Hindi)**, and **English**).

---

## 🏛️ Project Directory Structure

```text
vyapar-mitra-agent/
│
├── backend/                               # FastAPI Python Core Backend & AI Logic
│   ├── agent.py                           # Multi-Mode Agent Orchestrator, Multilingual NLP Router
│   ├── knowledge_base.json                # Curated RAG Data (PM SVANidhi, Mudra, ONDC, APMC Mandi)
│   ├── ledger.py                          # NLP Micro-Accounting, Multi-Period P&L Engine (Devanagari enabled)
│   ├── main.py                            # RESTful API Endpoints & Static File Server
│   ├── ondc_manager.py                    # Beckn Protocol Compliant ONDC Retail Catalogue Generator
│   ├── poster_generator.py                # Standee Banner & SVG Poster Generator
│   ├── qr_generator.py                    # UPI QR Code Generator with Base64 Payload
│   ├── rag_engine.py                      # Retrieval-Augmented Generation Knowledge Base Engine
│   └── schemes_application.py             # PM SVANidhi Tranche 1-3 Official Loan Application Kit
│
├── frontend/                              # Glassmorphic Multilingual Frontend
│   ├── app.js                             # Full Client Logic, I18N Engine, Chart.js Controller, Speech API
│   ├── index.html                         # Premium Responsive Glassmorphic UI & Interactive Dashboard
│   └── styles.css                         # Glowing Theme, Glassmorphism, Print Layout, Animations
│
├── tests/                                 # Automated Test Suite
│   └── test_agent.py                      # 7 Comprehensive Unit & Integration Tests (100% Passing)
│
├── requirements.txt                       # Python Dependencies (FastAPI, Uvicorn, QRCode, Pytest, etc.)
├── run.py                                 # Single-Command Application Runner
└── README.md                              # Comprehensive Documentation & Architecture Guide
```

---

## 🎯 8 Core Intelligent Modes & Capabilities

| Mode # | Mode Name | Description | Key Features |
|---|---|---|---|
| **Mode 1** | **Digital Onboarding Kit** | Creates instant digital footprint for informal vendors | Business description, Google Maps listing, UPI integration steps, daily pricing strategy |
| **Mode 2** | **Digital Readiness Score** | 0–100 Credit & Digital Maturity Score | Evaluates UPI adoption, Maps presence, ONDC catalog, and government scheme registration |
| **Mode 3** | **Micro-Accounting Ledger** | Voice & Natural Language Bookkeeping | Real-time sales/expense logging, Devanagari numerals parsing (`०-९`), Daily/Weekly/Monthly/Yearly charts |
| **Mode 4** | **Hyperlocal Mandi Intelligence** | APMC Wholesale & Footfall Insights | Wholesale vs. retail margins for seasonal fruits/vegetables, optimal selling windows |
| **Mode 5** | **WhatsApp Broadcast** | Vendor Customer Engagement | Staged 1-tap WhatsApp broadcast messages with offers, UPI ID, and interactive menu |
| **Mode 6** | **PM SVANidhi Loan Application** | Micro-Credit Formalization Kit | Auto-generates application kit for ₹15,000 / ₹20,000 / ₹50,000 loans with 7% interest subsidy |
| **Mode 7** | **ONDC Store Catalogue** | Beckn-Protocol Retail Onboarding | Exports structured JSON catalogue with items, prices, and UPI payment bindings |
| **Mode 8** | **Printable QR Standee & Posters** | Stall Marketing Asset Generator | High-resolution printable SVG/PNG standees with embedded UPI QR codes |

---

## 🌐 Multilingual & Devanagari Processing Engine

- **Supported Languages**: **मराठी (Marathi)**, **हिंदी (Hindi)**, **English**.
- **Dynamic UI Localization**: Instantly translates all navigation tabs, action chips, input placeholders, welcome cards, and metrics without page reload.
- **Voice Recognition Integration**: Automatically configures Web Speech API with regional locales (`mr-IN`, `hi-IN`, `en-IN`).
- **Devanagari Numeral Normalization**: Seamlessly converts `०१२३४५६७८९` to `0123456789` for accurate calculation in natural speech transactions (e.g., *"आज केळी विकली ₹५०० आणि चहा खर्च ₹८०"*).

---

## 🔌 API Endpoints Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check & service status |
| `POST` | `/api/chat` | Main conversational AI agent intent routing & localized response |
| `GET` | `/api/reports/sales` | Periodic sales and profit analytics (`daily`, `weekly`, `monthly`, `yearly`) |
| `GET` | `/api/reports/export` | Download complete accounting ledger as CSV |
| `POST` | `/api/schemes/apply-pmsvanidhi` | Generate formal PM SVANidhi loan application kit |
| `GET` | `/api/ondc/catalogue` | Generate Beckn protocol retail schema for ONDC |
| `POST` | `/api/poster/generate` | Generate printable stall poster SVG with QR code |
| `POST` | `/api/qr/generate` | Generate base64 dynamic/static UPI QR code |
| `GET` | `/api/vendor/profile` | Retrieve current vendor configuration & profile |
| `POST` | `/api/vendor/profile` | Update vendor store details, discount rules, profit targets |

---

## ⚡ Quick Start & Running Guide

### 1. Prerequisites
Ensure **Python 3.9+** is installed on your system.

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Run Automated Tests
```powershell
pytest -v
```

### 4. Launch the Platform
```powershell
python run.py
```
Open your browser and navigate to: **`http://localhost:8000`**

---

## 🧪 Verification & Test Suite
All 7 unit and integration tests run in under 1 second:
- `test_rag_knowledge_base`: Validates PM SVANidhi and MSME knowledge base.
- `test_multi_period_reports`: Tests daily, weekly, monthly, and yearly chart aggregations.
- `test_pmsvanidhi_application`: Tests loan tranche generation and required document checklists.
- `test_ondc_store_catalogue`: Tests Beckn schema catalogue structure.
- `test_api_endpoints`: Verifies all REST endpoints and CSV exports.
- `test_multilingual_marathi_hindi_support`: Tests Marathi/Hindi natural language parsing and Devanagari numerals.
- `test_chat_multilingual_api`: Tests end-to-end multilingual `/api/chat` responses.

