# 🚀 AI-Enhanced Lead Scoring – Caprae Capital AI-Readiness Challenge

## Approach

This project focuses on making lead scoring faster and more effective by building a simple, rule-based tool tailored for Caprae Capital’s SaaS and M&A needs. Instead of using complex machine learning models or labeled data, I created a clear and easy-to-understand system that scores leads based on business logic and industry knowledge.

## Scoring Logic

Each lead is scored based on five key aspects:
- **Company Size** (25%) – Based on number of employees. Mid-sized companies are ideal for M&A deals.
- **Industry Attractiveness** (30%) – Industries like SaaS, Fintech, and HealthTech get higher scores based on Caprae’s preferences.
- **Financial Indicators** (25%) – Includes revenue, profit, and growth if available.
- **Website Quality & Tech Signals** (10%) – Looks at website domains (e.g., .io, .ai) and keywords related to tech.
- **Market Position** (10%) – Based on company name, keywords, and how well the company fits in its industry.

These scores are combined using weighted averages. The final score may go up or down depending on other business signals—like if the company is in a high-growth sector (bonus) or has poor web presence (penalty).

## Preprocessing

Before scoring, the uploaded data is cleaned and prepared using `pandas`, including:
- Fixing missing or messy values.
- Estimating company age from the founding year.
- Analyzing website URLs and detecting keywords for scoring.
- Removing duplicate entries and standardizing the data format.

## Explainability & UX

Each scored lead includes:
- **Scoring rationale** – Simple explanation of why a lead got its score.
- **Risk factors** – Warnings if some data is missing or if the lead looks weak.
- **Growth indicators** – Positive signs like fast growth or strong market fit.

These details make it easier for users to filter, understand, and focus on the most promising leads using the streamlit dashboard.

## Performance

This tool runs fast—even with 10,000+ rows—and is easy to improve or expand. I also added a percentile-based adjustment to spread out the scores better, so leads don’t all fall into just one category like “Medium.”

## Why This Matters

The tool is designed with real M&A lead generation in mind. Instead of using complex black-box models, it applies clear business logic, helping teams spot high-potential leads quickly and confidently.

---

*Built by Veronica Dwiyanti | [Live App ↗️](https://lead-ranker-caprae.streamlit.app/)*
