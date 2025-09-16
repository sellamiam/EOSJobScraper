<br>

Features
Automated Scraping: Uses Selenium to navigate and scrape job listings from the Eos Energy careers website.

Persistent Storage: Stores job data in a local SQLite database (eos_jobs.db), with a unique constraint on the job link to prevent duplicate entries.

Google Sheets Integration: Appends new job data to a designated Google Sheet, making it easy to view and share.

Error Handling: Includes error handling for scraping and database operations to ensure the script runs smoothly even if no new jobs are found or the website structure changes.

<br>

Getting Started
1. Prerequisites
Python 3.x: Make sure you have a compatible version of Python installed.

ChromeDriver: The script uses Selenium with ChromeDriver. You need to download the correct version for your operating system and Chrome browser version.

Google Cloud Credentials: To connect to Google Sheets, you need a service account and a gspread_creds.json file. Follow the official gspread documentation to set this up.

2. Installation
Clone the repository:

Bash

git clone https://github.com/your-username/EOSJobScraper.git
cd EOSJobScraper
Install the required libraries:

Bash

pip install -r requirements.txt
Place ChromeDriver: Move the chromedriver executable to the location specified in the script (CHROMEDRIVER_PATH).

Add Google Credentials: Place your gspread_creds.json file in the correct directory as specified in the script.

<br>

Usage
To run the scraper, simply execute the Python script from your terminal.

Bash

python eos_jobs_scraper.py
The script will:

Launch a Chrome browser instance.

Scrape all current job listings.

Save the data to eos_jobs.db.

Append the data to your Google Sheet.

<br>

Project Structure
eos_jobs_scraper.py: The main Python script containing the scraping logic, database operations, and Google Sheets integration.

eos_jobs.db: The SQLite database file where job data is stored.

gspread_creds.json: Your Google Sheets service account credentials file (kept locally and not committed to Git).

requirements.txt: A list of Python libraries required for the project.

<br>

Troubleshooting
Script fails to run: Check that CHROMEDRIVER_PATH and GOOGLE_CREDS_FILE are correctly configured in the script.

Database not updating: If the Google Sheet is updating but the database is not, it is likely that the scraper is finding no new jobs. The database's unique key constraint prevents the insertion of duplicate entries, which is the intended behavior.

NoSuchElementException: The website's HTML structure has likely changed. You will need to inspect the page and update the CSS selectors in the scrape_jobs function.

<br>

Contributing
Feel free to open an issue or submit a pull request if you have suggestions for improvements or bug fixes.







