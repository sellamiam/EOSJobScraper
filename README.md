EOS Job Scraper
Disclaimer

It should work just fine. I run it regularly myself, but if anything breaks I take no responsibility. Use at your own risk.

Prerequisites

I use Google Chrome. It should work elsewhere but if it doesn’t, try with Chrome.

You need:

Python 3.x

ChromeDriver (must match your Chrome + OS version)

Google service account + gspread_creds.json (follow gspread docs
)

Tutorial
Installation
git clone https://github.com/your-username/EOSJobScraper.git
cd EOSJobScraper
pip install -r requirements.txt


Place chromedriver at the location set in CHROMEDRIVER_PATH.

Put gspread_creds.json where GOOGLE_CREDS_FILE points.

Usage

Run it like this:

python eos_jobs_scraper.py


What happens:

Chrome opens

Script scrapes EOS Energy job listings

Results saved in eos_jobs.db

New jobs appended to Google Sheet

Filtering / Options

Database has a unique key on job link → prevents duplicates automatically.

If the site changes and you get errors (NoSuchElementException), update the CSS selectors in scrape_jobs().

If the Google Sheet updates but the DB doesn’t → no new jobs found, not a bug.

Troubleshooting

Script fails to run → check CHROMEDRIVER_PATH + GOOGLE_CREDS_FILE.

Database not updating → duplicates are blocked by design.

Selectors broken → update scrape_jobs() with the new structure.

Support

Open an issue or pull request on GitHub.

Other

If you want to contribute, PRs are welcome.
