EOS Job Scraper
Python scraper that collects job listings from the EOS Energy careers website, stores them in SQLite, and syncs them with Google Sheets.
🚀 Features
Automated Scraping: Selenium-based job scraper.
Persistent Storage: Saves jobs to eos_jobs.db with duplicate prevention.
Google Sheets Integration: Appends new jobs to a Google Sheet.
Error Handling: Handles site changes, missing data, and duplicates.
🛠 Setup
Prerequisites
Python 3.x
ChromeDriver (matching your OS + Chrome version)
Google service account + gspread_creds.json (see gspread docs: https://docs.gspread.org/)
Installation
Clone the repository and install dependencies:
git clone https://github.com/your-username/EOSJobScraper.git cd EOSJobScraper pip install -r requirements.txt
Configuration:
• Place ChromeDriver at the path specified in CHROMEDRIVER_PATH. • Place gspread_creds.json where GOOGLE_CREDS_FILE points.
▶️ Usage
Run the scraper:
python eos_jobs_scraper.py
The script will: 1. Launch Chrome 2. Scrape all current job listings 3. Save data to eos_jobs.db 4. Append data to Google Sheets
📂 Project Structure
EOSJobScraper/ ├── eos_jobs_scraper.py   # main script ├── eos_jobs.db           # SQLite DB ├── gspread_creds.json    # Google credentials (local only) └── requirements.txt      # dependencies
⚠️ Troubleshooting
Script fails → Check CHROMEDRIVER_PATH and GOOGLE_CREDS_FILE.
DB not updating → Likely no new jobs; duplicates are blocked.
NoSuchElementException → Update CSS selectors in scrape_jobs().
🤝 Contributing
PRs and issues welcome!
