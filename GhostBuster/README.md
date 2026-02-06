# VeriJob AI - Ghost Job & Scam Detector 🕵️‍♂️🚫

**Stop Applying to Ghost Jobs.**  
VeriJob AI employs autonomous agents to verify job listing integrity in real-time. It cross-references hiring patterns, layoff data, and metadata anomalies to give you a "Truth Score" for every job post.

![VeriJob AI Dashboard](verijob_dashboard_preview.png)

## 🚀 Key Features

- **🛡️ Integrity Score**: AI analysis of job descriptions to detect "ghost job" templates, vague requirements, and evergreen listings.
- **📰 Reality Check**: Cross-references company news (layoffs, hiring freezes) and Reddit sentiment (scam reports, ghosting stories).
- **🧩 Browser Extension**: Auto-verifies jobs directly on LinkedIn and Indeed.
- **🔍 Smart Search**: Filters out irrelevant noise to show you only the signals that matter.

## 🛠️ Stack

- **Frontend**: Next.js 14, Tailwind CSS, Framer Motion
- **Backend**: FastAPI, Python, LangChain, LangGraph
- **AI**: Llama 3 (via Groq), Tavily Search API
- **Extension**: Chrome Extension Manifest V3

## 📦 Installation

### 1. Web Application
```bash
cd frontend
npm install
npm run dev
# Open http://localhost:3000
```

### 2. Backend API
```bash
cd backend
pip install -r requirements.txt
python run.py
# Server running at http://localhost:8000
```

### 3. Chrome Extension
1. Go to `chrome://extensions`
2. Enable **Developer Mode**
3. Click **Load Unpacked**
4. Select the `extension` folder from this repo.

## 🔑 Configuration
Create a `.env` file in `backend/`:
```env
TAVILY_API_KEY=tvly-...
GROQ_API_KEY=gsk_...
```

## 🤝 Contributing
Built by [Pranit Satnurkar](https://github.com/Pranit-satnurkar).
Contributions welcome!
