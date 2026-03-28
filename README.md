# ₿ Bitcoin Live Dashboard

A simple, real-time Bitcoin price dashboard built with **Python + Streamlit**.

## Features

- 💰 Live Bitcoin price (USD)
- 📈 24-hour % change, market cap, and volume
- 📊 7-day interactive price chart (Plotly)
- 🔄 One-click refresh button
- 🔐 API key stored securely via `.env` (never committed to GitHub)

---

## Tech Stack

| Library | Purpose |
|---|---|
| `streamlit` | Dashboard UI |
| `requests` | HTTP API calls |
| `pandas` | Data handling |
| `plotly` | Interactive charts |
| `python-dotenv` | Load `.env` secrets |

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/username/bitcoin-dashboard.git
cd bitcoin-dashboard
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your API key

Create a `.env` file in the project root (copy from the example):

```bash
cp .env.example .env
```

Open `.env` and replace the placeholder with your real key:

```
API_KEY=your_coinmarketcap_api_key_here
```

> **Get a free API key** at [https://coinmarketcap.com/api/](https://coinmarketcap.com/api/)

> ⚠️ `.env` is listed in `.gitignore` — it will **never** be pushed to GitHub.

### 5. Run the dashboard

```bash
streamlit run app.py
```

The app opens automatically at [http://localhost:8501](http://localhost:8501).

---

## Project Structure

```
bitcoin-dashboard/
├── app.py            # Main Streamlit application
├── requirements.txt  # Python dependencies
├── .env              # Your secret API key (NOT committed)
├── .env.example      # Safe template to share on GitHub
├── .gitignore        # Excludes .env and cache files
└── README.md         # This file
```

---

## Push to GitHub

```bash
git init
git add .
git commit -m "Bitcoin live dashboard"
git branch -M main
git remote add origin https://github.com/username/bitcoin-dashboard.git
git push -u origin main
```

> Replace `username` with your actual GitHub username.

---

## Security Notes

- The `.env` file is **excluded from Git** via `.gitignore`.
- Never paste your API key directly into `app.py`.
- Rotate your API key immediately if you accidentally commit it.
