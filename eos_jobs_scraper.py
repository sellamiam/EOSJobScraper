import time
import datetime
import sqlite3
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os



# --- CONFIG ---
URL = "https://eosenergystorage.wd1.myworkdayjobs.com/EoS"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
GOOGLE_CREDS_FILE = "/Users/msellamia/Scripts/cred/gspread_creds.json"
SHEET_NAME = "eos_jobs"
DB_FILE = os.path.join(SCRIPT_DIR, "eos_jobs.db")
CHROMEDRIVER_PATH = "/Users/msellamia/Downloads/chromedriver-mac-arm64/chromedriver"

HEADERS = ["Title", "Location", "Date Posted", "Link", "Scrape Date"]

# --- GOOGLE SHEETS SETUP ---
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDS_FILE, scope)
client = gspread.authorize(creds)

try:
    sheet = client.open(SHEET_NAME).sheet1
except gspread.SpreadsheetNotFound:
    sheet = client.create(SHEET_NAME).sheet1
    print(f"Created new sheet: {SHEET_NAME}")

# Ensure headers are in the first row
sheet_values = sheet.get_all_values()
if not sheet_values or sheet_values[0] != HEADERS:
    sheet.clear()
    sheet.append_row(HEADERS)
    print("Headers added to the sheet.")

# --- DATABASE SETUP ---
conn = sqlite3.connect(DB_FILE)
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        location TEXT,
        date_posted TEXT,
        link TEXT UNIQUE,
        scrape_date TEXT
    )
''')
conn.commit()

# --- SCRAPER ---
def scrape_jobs():
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service)
    driver.get(URL)

    data = []
    scraped_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    WebDriverWait(driver, 60).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.css-1q2dra3"))
    )

    pagination_buttons = driver.find_elements(By.CSS_SELECTOR, "button[data-uxi-widget-type='paginationPageButton']")
    total_pages = len(pagination_buttons) if pagination_buttons else 1

    for page in range(1, total_pages + 1):
        WebDriverWait(driver, 60).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.css-1q2dra3"))
        )

        job_list = driver.find_elements(By.CSS_SELECTOR, "li.css-1q2dra3")

        for job in job_list:
            try:
                title = job.find_element(By.CSS_SELECTOR, "a[data-automation-id='jobTitle']").text
            except:
                title = ""
            try:
                location = job.find_element(By.CSS_SELECTOR, "div.css-248241").text.replace("locations\n", "").strip()
            except:
                location = ""
            try:
                posted = job.find_element(By.CSS_SELECTOR, "div.css-zoser8").text.replace("posted on\n", "").strip()
            except:
                posted = ""
            try:
                link_tag = job.find_element(By.CSS_SELECTOR, "a[data-automation-id='jobTitle']")
                link = link_tag.get_attribute("href")
            except:
                link = ""

            data.append({
                "title": title,
                "location": location,
                "date_posted": posted,
                "link": link,
                "scrape_date": scraped_date
            })

        if page < total_pages:
            try:
                next_btn = driver.find_element(By.XPATH, f"//button[@aria-label='page {page + 1}']")
                driver.execute_script("arguments[0].click();", next_btn)
                time.sleep(60)
            except:
                break

    driver.quit()
    return data

# --- SAVE TO SQLITE ---
def save_to_db(jobs):
    for job in jobs:
        try:
            c.execute('''
                INSERT INTO jobs (title, location, date_posted, link, scrape_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (job['title'], job['location'], job['date_posted'], job['link'], job['scrape_date']))
        except sqlite3.IntegrityError:
            continue
    conn.commit()

# --- SAVE TO GOOGLE SHEET ---
def save_to_google_sheet(jobs):
    try:
        jobs_to_append = [
            [job['title'], job['location'], job['date_posted'], job['link'], job['scrape_date']]
            for job in jobs
        ]
        
        if jobs_to_append:
            sheet.append_rows(jobs_to_append)
            print(f"Appended {len(jobs_to_append)} jobs to the Google Sheet.")
        else:
            print("No jobs to append to the Google Sheet.")

    except gspread.exceptions.APIError as e:
        print(f"An API error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    jobs = scrape_jobs()
    save_to_db(jobs)
    save_to_google_sheet(jobs)
    print(f"{len(jobs)} jobs scraped, saved to DB and Google Sheet.")
    conn.close()