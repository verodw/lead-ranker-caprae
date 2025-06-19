# Lead Ranker for Caprae Capital

This is a lightweight AI-enhanced lead scoring tool built for the Caprae Capital AI-Readiness Challenge.  
The goal is to enhance lead generation capabilities by prioritizing high-impact leads using an intelligent ranking system.

🚀 **Live Demo**: [Click here to try the app ↗️](https://lead-ranker-caprae.streamlit.app/)

<img width="1465" alt="Dashboard Preview" src="https://github.com/user-attachments/assets/b5ae4e5f-e869-44e2-a03f-b408d9a6aa16" />

## Features

- **Automated Lead Scoring**: Assigns scores to leads based on historical, behavioral, and demographic data using machine learning techniques.
- **Data Cleaning & Deduplication**: Ensures input data is clean and free from duplicates to improve scoring accuracy.
- **Customizable Scoring Criteria**: Allows manual adjustment of scoring weights to suit different business objectives or industries.
- **Interactive Dashboard**: Built with Streamlit for intuitive data upload, score visualization, and lead exploration.
- **Export & Integration Ready**: Enables CSV/Excel export for seamless integration into sales pipelines or CRM tools.
- **Basic Reporting**: Provides visuals for score distributions and top-ranked leads, enabling fast decision-making.

## Tech Stack

| Component          | Technology                  |
|--------------------|------------------------------|
| Frontend & Backend | Streamlit                    |
| Machine Learning   | scikit-learn                 |
| Data Handling      | pandas                       |
| Data Storage       | CSV                          |
| Deployment         | Streamlit Cloud              |

## Usage

1. **Upload** your lead data (CSV format) through the dashboard.
2. The tool will automatically **clean**, **deduplicate**, and **score** each lead.
3. Use the interactive UI to **adjust scoring criteria** (e.g., industry relevance, company size).
4. **View and filter** leads by score and other attributes.
5. **Export** the final scored list as CSV or Excel for your sales workflow.

## 📂 Sample Dataset

Test the app using sample organization datasets:

- [organizations-100.csv](https://github.com/verodw/lead-ranker-caprae/blob/deploy-veronica/sample_data/organizations-100.csv)
- [organizations-1000.csv](https://github.com/verodw/lead-ranker-caprae/blob/deploy-veronica/sample_data/organizations-1000.csv)
- [organizations-10000.csv](https://github.com/verodw/lead-ranker-caprae/blob/deploy-veronica/sample_data/organizations-10000.csv)

📎 Source: [Datablist – Download Sample CSV Files](https://www.datablist.com/learn/csv/download-sample-csv-files)
