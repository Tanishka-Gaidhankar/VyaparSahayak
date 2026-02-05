# VyaaparSahayak - Business Intelligence Platform

**VyaaparSahayak** is an AI-powered business intelligence platform designed to help startups and small businesses manage their operations, analyze risks, and grow through intelligent marketing strategies.

---

## 🚀 Features

### Core Modules
- **📊 Dashboard** - Real-time business metrics and analytics
- **📦 Product Management** - Track inventory, costs, and pricing
- **🛒 Order Management** - Process orders across multiple sales channels
- **🏭 Production Tracking** - Monitor production batches and costs
- **📈 Marketing Analytics** - Channel-wise sales performance
- **🎯 Government Schemes** - AI-matched funding opportunities
- **⚠️ Risk Analysis** - AI-powered business risk detection

### AI-Powered Features
- **🤖 AI Audience Matching** - Identify target audiences and optimal platforms
- **✨ AI Content Optimization** - Generate platform-specific marketing content
- **📊 Market Research** - Real-time market trends via SerpAPI (optional)

---

## 📋 Prerequisites

Before running this project, ensure you have:

- **Python 3.10+** installed
- **Node.js 18+** and **npm** installed
- **Git** (optional, for cloning)

---

## 🛠️ Installation & Setup

### Step 1: Clone or Download the Project

```bash
# If using Git
git clone <repository-url>
cd VyaaparSahayak

# Or download and extract the ZIP file
```

---

### Step 2: Backend Setup

#### 2.1 Navigate to Backend Directory
```bash
cd backend
```

#### 2.2 Install Python Dependencies
```bash
pip install -r requirements.txt
```

#### 2.3 Configure API Keys

Create or edit the `.env` file in the `backend` folder:

```bash
# backend/.env

# GROQ API Key (Required for AI features)
GROQ_API_KEY=your_groq_api_key_here

# SerpAPI Key (Optional - for enhanced market research)
SERPAPI_KEY=your_serpapi_key_here
```

**How to get API keys:**

1. **GROQ API Key** (Free):
   - Visit: https://console.groq.com/keys
   - Sign up for a free account
   - Create a new API key
   - Copy and paste into `.env`

2. **SerpAPI Key** (Optional, Free tier available):
   - Visit: https://serpapi.com/
   - Sign up for free account (100 searches/month)
   - Get your API key
   - Copy and paste into `.env`

#### 2.4 Initialize Database

The database will be created automatically when you first run the server. It uses SQLite (`app.db`).

#### 2.5 Start Backend Server

```bash
python run_server.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**Keep this terminal running!**

---

### Step 3: Frontend Setup

Open a **new terminal window** (keep backend running).

#### 3.1 Navigate to Frontend Directory
```bash
cd frontend/vyaaparsahayak-insights-main
```

#### 3.2 Install Node Dependencies
```bash
npm install
```

#### 3.3 Start Frontend Development Server
```bash
npm run dev
```

You should see:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

---

### Step 4: Access the Application

1. **Open your browser** and go to: **http://localhost:5173**
2. **Complete onboarding** - Fill in your business profile
3. **Start using the platform!**

---

## 📁 Project Structure

```
VyaaparSahayak/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── run_server.py          # Server startup script
│   ├── requirements.txt       # Python dependencies
│   ├── .env                   # API keys (create this)
│   ├── app.db                 # SQLite database (auto-created)
│   └── schemes.json           # Government schemes data
│
├── frontend/
│   └── vyaaparsahayak-insights-main/
│       ├── src/
│       │   ├── pages/         # React pages
│       │   │   ├── Dashboard.tsx
│       │   │   ├── Products.tsx
│       │   │   ├── Orders.tsx
│       │   │   ├── Production.tsx
│       │   │   ├── Marketing.tsx
│       │   │   ├── AIGrowth.tsx      # AI Features
│       │   │   ├── Schemes.tsx
│       │   │   └── RiskAnalysis.tsx
│       │   ├── components/    # Reusable components
│       │   ├── lib/
│       │   │   └── api.ts     # API client
│       │   └── App.tsx        # Main app component
│       ├── package.json
│       └── vite.config.ts
│
├── AI_FEATURES_DOCUMENTATION.md
├── FRONTEND_INTEGRATION.md
└── README.md (this file)
```

---

## 🎯 Quick Start Guide

### First Time Setup (5 minutes)

1. **Install dependencies:**
   ```bash
   # Backend
   cd backend
   pip install -r requirements.txt
   
   # Frontend (new terminal)
   cd frontend/vyaaparsahayak-insights-main
   npm install
   ```

2. **Get GROQ API Key:**
   - Go to https://console.groq.com/keys
   - Sign up and create API key
   - Add to `backend/.env`

3. **Start both servers:**
   ```bash
   # Terminal 1 - Backend
   cd backend
   python run_server.py
   
   # Terminal 2 - Frontend
   cd frontend/vyaaparsahayak-insights-main
   npm run dev
   ```

4. **Open browser:** http://localhost:5173

---

## 🔧 Common Issues & Solutions

### Issue: Port 8000 already in use

**Solution:**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /F /PID <PID_NUMBER>

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### Issue: Frontend can't connect to backend

**Check:**
1. Backend is running on http://127.0.0.1:8000
2. Check `frontend/src/lib/api.ts` - `API_BASE_URL` should be `http://127.0.0.1:8000`
3. CORS is enabled in backend (already configured)

### Issue: 401 Error on AI Features

**Solution:**
- Your GROQ API key is invalid or expired
- Get a new key from https://console.groq.com/keys
- Update `backend/.env`
- Restart backend server

### Issue: Database errors

**Solution:**
```bash
# Delete and recreate database
cd backend
rm app.db
python run_server.py  # Will recreate database
```

---

## 📚 API Documentation

### Backend API Endpoints

**Base URL:** `http://127.0.0.1:8000`

#### Products
- `GET /products` - List all products
- `POST /products` - Create new product

#### Orders
- `POST /orders` - Create new order

#### Dashboard
- `GET /dashboard` - Get dashboard metrics
- `GET /dashboard/products` - Product performance
- `GET /dashboard/channel-wise` - Channel-wise sales
- `GET /dashboard/sales-summary` - Sales summary

#### AI Features
- `POST /ai/audience-matching` - Get audience and platform recommendations
- `POST /ai/content-optimization` - Generate optimized content

#### Schemes
- `GET /schemes` - List all schemes
- `GET /startup-profile/{id}/matched-schemes` - Get matched schemes

#### Risk Analysis
- `POST /risk-analysis` - Run risk analysis
- `GET /risk-analysis/{id}` - Get risk report

---

## 🎨 Using the Platform

### 1. Complete Onboarding
- Fill in your business details
- This creates your startup profile

### 2. Add Products
- Go to **Products** page
- Add your products with costs and pricing

### 3. Create Orders
- Go to **Orders** page
- Create orders for different sales channels

### 4. Track Production
- Go to **Production** page
- Log production batches
- View production insights

### 5. Analyze Performance
- **Dashboard** - Overall metrics
- **Marketing** - Channel performance
- **Risk Analysis** - Business risks

### 6. Use AI Growth Features
- Go to **AI Growth** page
- **Tab 1:** Analyze target audience and get platform recommendations
- **Tab 2:** Generate optimized content for specific platforms

### 7. Find Funding
- Go to **Schemes** page
- View government schemes matched to your profile

---

## 🔑 Environment Variables

### Backend `.env` File

```bash
# Required
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxx

# Optional (enhances market research)
SERPAPI_KEY=xxxxxxxxxxxxxxxxxxxxx
```

---

## 🧪 Testing

### Test Backend API
```bash
cd backend
python -m pytest  # If tests are available
```

### Test AI Features
```bash
cd VyaaparSahayak
python test_ai_features.py
```

---

## 📦 Dependencies

### Backend (Python)
- FastAPI - Web framework
- Uvicorn - ASGI server
- SQLAlchemy - Database ORM
- Pydantic - Data validation
- GROQ - AI API client
- SerpAPI - Market research (optional)
- python-dotenv - Environment variables

### Frontend (Node.js)
- React - UI framework
- TypeScript - Type safety
- Vite - Build tool
- TailwindCSS - Styling
- shadcn/ui - UI components
- TanStack Query - Data fetching
- React Router - Navigation

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## 📄 License

This project is licensed under the MIT License.

---

## 🆘 Support

For issues or questions:
1. Check the **Common Issues** section above
2. Review `AI_FEATURES_DOCUMENTATION.md` for AI features
3. Review `FRONTEND_INTEGRATION.md` for frontend details

---

## 🎉 You're All Set!

Your VyaaparSahayak platform should now be running. Start by:
1. Completing your business profile
2. Adding your first product
3. Creating your first order
4. Exploring the AI Growth features!

**Happy Business Building! 🚀**
