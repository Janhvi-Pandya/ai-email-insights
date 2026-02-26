# AI Email Insights & Summarization Tool  
**Status: Currently in active development (not final version)**

An AI-powered email analytics and summarization system designed to extract structured insights from large volumes of unstructured email data using Large Language Models (LLMs).

This project explores how Generative AI can support enterprise analytics workflows by transforming raw email communication into actionable intelligence for operational and business decision-making.

---

# Project Goal

Organizations receive thousands of emails related to:

- Customer feedback & complaints  
- Operational issues  
- Incident reports  
- Maintenance & asset updates  
- Internal coordination  

Manually reviewing these emails is slow and inefficient.

This project demonstrates how AI can automatically:
- Summarize emails  
- Extract action items  
- Detect urgency & sentiment  
- Identify recurring issues  
- Generate structured analytics for decision support  

---

#  Current Features (Work in Progress)

### AI Processing
- Email summarization using LLMs  
- Topic classification (operations, maintenance, customer issues, etc.)  
- Urgency detection (low / medium / high)  
- Sentiment analysis  
- Action item extraction  
- Structured JSON outputs for analytics pipelines  

### Analytics Dashboard
- Topic frequency tracking  
- Urgency distribution  
- Sentiment trends  
- Action item frequency analysis  
- Export results to CSV/JSON  

### Technical Stack
- Python  
- Streamlit (dashboard UI)  
- Pandas (data processing)  
- OpenAI API (LLM integration – optional)  
- Pydantic (structured outputs)  

---

#  Project Status

**This project is currently being built and refined.**

It is not a finished production system yet.

Planned improvements:
- Improved prompt engineering & accuracy  
- Enhanced entity extraction  
- Vector search for semantic clustering  
- Power BI integration  
- Performance optimization  
- Deployment-ready version  

This repository reflects an **active development portfolio project** demonstrating applied GenAI + analytics.

---

#  How to Run Locally

## 1. Clone repository

git clone https://github.com/YOUR-USERNAME/ai-email-insights.git
cd ai-email-insights

## 2. Create Virtual Environment

### Windows
python -m venv venv  
venv\Scripts\activate  

### Mac/Linux
python3 -m venv venv  
source venv/bin/activate  

---

## 3. Install Dependencies
pip install -r requirements.txt  

---

## 4. (Optional) Add OpenAI API Key for Real AI Summaries

### Windows (PowerShell)
$env:OPENAI_API_KEY="your_key_here"

### Mac/Linux
export OPENAI_API_KEY="your_key_here"

If no API key is added, the app will run in offline demo mode.

---

## 5. Run the App
streamlit run app.py  

Then open your browser and go to:  
http://localhost:8501

---

# Project Structure

ai-email-insights/  
│  
├── app.py                # Streamlit dashboard  
├── llm.py                # LLM processing logic  
├── analysis.py           # Analytics & KPIs  
├── sample_emails.csv     # Demo dataset  
├── requirements.txt  
└── README.md  

---

# Data & Privacy Note

This project uses synthetic or publicly available datasets for demonstration purposes only.  
No real private or sensitive email data is included.

---

#  Author

Janhvi Pandya  
Computer Science — Data Analytics  
University of Victoria  

GitHub: https://github.com/YOUR-USERNAME  
LinkedIn: (add link)

---

# Future Vision

This project is part of a broader exploration into:

- Enterprise AI workflow automation  
- Data analytics for operations & decision support  
- Data governance & structured insights  
- Generative AI in business intelligence  

---

# If You're a Recruiter or Reviewer

This project is currently under active development as part of my applied analytics & AI portfolio.  
Feedback and suggestions are always welcome.
