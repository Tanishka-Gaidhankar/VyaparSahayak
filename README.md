# VyaaparSahayak - AI-Powered Business Intelligence Platform

An intelligent platform for startups and small businesses to manage operations, analyze risks, and grow through AI-powered marketing strategies.

## 🚀 Features

- **📊 Dashboard** - Real-time business metrics and analytics
- **📦 Product & Order Management** - Track inventory and sales across channels
- **🏭 Production Tracking** - Monitor production batches and costs
- **🤖 AI Growth Tools** - Audience matching and content optimization
- **🎯 Government Schemes** - AI-matched funding opportunities
- **⚠️ Risk Analysis** - AI-powered business risk detection

---

## 🛠️ Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Tanishka-Gaidhankar/VyaaparSahayak.git
   cd VyaaparSahayak
   ```

2. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   
   # Create .env file with your API key
   echo "GROQ_API_KEY=your_groq_api_key_here" > .env
   
   # Start backend server
   python run_server.py
   ```
   Get your free GROQ API key: https://console.groq.com/keys

3. **Frontend Setup** (in a new terminal)
   ```bash
   cd frontend/vyaaparsahayak-insights-main
   npm install
   npm run dev
   ```

4. **Access the app**: http://localhost:5173

---

## 📁 Project Structure

```
VyaaparSahayak/
├── backend/          # FastAPI backend
│   ├── main.py
│   └── .env         # API keys
└── frontend/        # React frontend
    └── vyaaparsahayak-insights-main/
```

---

## 🔑 API Key Setup

Create `backend/.env`:
```bash
GROQ_API_KEY=your_groq_api_key_here
SERPAPI_KEY=your_serpapi_key_here  # Optional
```

---

## 🆘 Common Issues

**Port 8000 in use?**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /F /PID <PID_NUMBER>
```

**Database errors?**
```bash
cd backend
rm app.db
python run_server.py
```

---

## 📄 License

MIT License

---

**Happy Business Building! 🚀**