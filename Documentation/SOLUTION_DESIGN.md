# 🏗️ Solution Design: VyaaparSahayak

## 1. High-Level Architecture
VyaaparSahayak follows a **Modern 3-Tier Microservices-Ready Architecture**, optimized for speed, scalability, and AI integration.

```mermaid
graph TD
    User[MSME User] -->|HTTPS| CDN[CDN / Edge]
    CDN --> Frontend[Frontend (React + Vite)]
    Frontend -->|REST API| Backend[Backend API Service (FastAPI)]
    
    subgraph "Core Business Logic"
        Backend -->|Auth & Logic| ServiceOrders[Order Service]
        Backend -->|Auth & Logic| ServiceProduct[Product Service]
        Backend -->|Analysis| ServiceRisk[Risk Engine]
    end
    
    subgraph "Intelligence Layer"
        ServiceGrowth[AI Growth Service] -->|Prompt Engineering| LLM[GROQ API (Llama 3)]
        ServiceGrowth -->|Market Data| SerpAPI[Google Search API]
    end
    
    subgraph "Data Storage"
        Backend -->|Read/Write| DB[(SQLite / PostgreSQL)]
    end
    
    Backend --> ServiceGrowth
```

---

## 2. Technology Stack

| Component | Technology | Rationale |
| :--- | :--- | :--- |
| **Frontend** | React.js (Vite) | High performance, rich ecosystem, component-based UI. |
| **Styling** | Tailwind CSS + shadcn/ui | Rapid development, modern accessible UI components. |
| **Backend** | Python (FastAPI) | Fastest Python framework, native async support for AI calls, auto-documentation (Swagger). |
| **Database** | SQLite (Dev) / PostgreSQL (Prod) | Relational integrity for orders/inventory. SQLite for easy local setup. |
| **AI Model** | Llama 3.3 70B (via GROQ) | state-of-the-art reasoning at 1/10th the cost and 10x speed of GPT-4. |
| **Market Data** | SerpAPI | Real-time google search results for up-to-date market trends. |

---

## 3. Core Modules & Data Flow

### A. Operations Module (The Backbone)
*   **Purpose:** Record and track day-to-day business activities.
*   **Data Models:** `Product`, `Order`, `ProductionBatch`.
*   **Flow:**
    1. User enters raw material & labor costs.
    2. System computes **Unit Economics** (Cost Price vs. Selling Price).
    3. Orders are logged; Inventory updates automatically (Master Inventory Lock).

### B. Intelligence Module (The AI Co-Pilot)
*   **Purpose:** Generate growth strategies and optimize content.
*   **Flow:**
    1. **Input:** User sends product details (e.g., "Handmade Soap").
    2. **Enrichment:** Backend calls **SerpAPI** to find top trends for "Handmade Soap India".
    3. **Reasoning:** Backend constructs a prompt with Product + Market Data → Sends to **GROQ AI**.
    4. **Output:** Structured JSON response (Target Audience, Platforms, Marketing Copy).

### C. Risk & Funding Module (The Safety Net)
*   **Purpose:** Predict failure points and find money.
*   **Flow:**
    1. **Risk Engine:** Scans internal DB (Sales Velocity, Inventory Levels).
    2. **Rule Engine:** Flags immediate risks (e.g., "Stockout in 5 days").
    3. **AI Layer:** Generates a mitigation plan (e.g., "Increase price by 5% to improve margin").
    4. **Scheme Matching:** Matches user profile (Women entrepreneur, SC/ST, Revenue < 5Cr) against Government Scheme Database JSON.

---

## 4. Scalability & Security Strategy

*   **Stateless Backend:** The FastAPI backend is stateless, allowing horizontal scaling behind a Load Balancer (e.g., Nginx) for high traffic.
*   **Async Processing:** AI calls to GROQ/SerpAPI are handled asynchronously, ensuring the UI never freezes while waiting for intelligence.
*   **API Key Hashing:** Sensitive keys are managed via environment variables and never exposed to the frontend.
*   **Modular Codebase:** Features (Orders, AI, Schemes) are decoupled in code, making it easy to turn into separate microservices later.
