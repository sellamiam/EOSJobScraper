import argparse
import logging
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sqlite3


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Analyze EOS job CSV and DB and produce plots")
    default_base = Path('/Users/mohamedsellamia/Scripts/EOSJobScraper') 
    p.add_argument('--csv', type=Path, default=default_base / 'eos_jobs.csv', help='Path to CSV file')
    p.add_argument('--db', type=Path, default=default_base / 'eos_jobs.db', help='Path to sqlite DB file')
    p.add_argument('--out', type=Path, default=default_base / 'eos_jobs_analysis.png', help='Output image path')
    p.add_argument('--show', action='store_true', help='Show plot interactively')
    p.add_argument('--log-level', default='INFO', help='Logging level')
    return p.parse_args()


def main(args: argparse.Namespace) -> int:
    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO),
                        format='%(levelname)s: %(message)s')
    logger = logging.getLogger(__name__)

    csv_file_path = args.csv
    db_file_path = args.db
    output_path = args.out

    # --- Load CSV ---
    if not csv_file_path.exists():
        logger.error('CSV file not found: %s', csv_file_path)
        return 2

    try:
        df = pd.read_csv(csv_file_path)
    except Exception as e:
        logger.exception('Failed to read CSV: %s', e)
        return 3

    # --- Data Cleaning ---
    def categorize_location(loc):
        """Categorizes job location into broader regions."""
        s = str(loc or '')
        if 'PA' in s:
            return 'PA'
        elif 'NJ' in s:
            return 'NJ'
        elif 'Remote' in s:
            return 'Remote'
        elif 'TX' in s:
            return 'TX'
        elif 'CA' in s:
            return 'CA'
        elif 'Locations' in s:
            return 'Multiple'
        else:
            return 'Other'

    # Use .loc to avoid SettingWithCopyWarning
    if 'Location' in df.columns:
        df.loc[:, 'Location_Category'] = df['Location'].apply(categorize_location)
    else:
        df.loc[:, 'Location_Category'] = 'Other'

    unique_jobs = df.drop_duplicates(subset=[c for c in ['Title', 'Location'] if c in df.columns])

    # --- Categorize jobs ---
    def categorize_job(title):
        """Categorizes job title into job families."""
        t = str(title or '').lower()
        if any(w in t for w in ['engineer', 'technician', 'developer', 'scientist', 'analyst']):
            return 'Engineering/Technical'
        elif any(w in t for w in ['manager', 'supervisor', 'lead', 'director']):
            return 'Management'
        elif any(w in t for w in ['specialist', 'coordinator', 'administrator', 'support', 'operations']):
            return 'Operations/Support'
        elif any(w in t for w in ['intern', 'temporary']):
            return 'Internship/Temporary'
        else:
            return 'Other'

    if 'Title' in unique_jobs.columns:
        unique_jobs.loc[:, 'Job_Category'] = unique_jobs['Title'].apply(categorize_job)
    else:
        unique_jobs.loc[:, 'Job_Category'] = 'Other'

    if 'Title' in df.columns:
        df.loc[:, 'Job_Category'] = df['Title'].apply(categorize_job)
    else:
        df.loc[:, 'Job_Category'] = 'Other'

    # --- Counts ---
    job_category_counts = unique_jobs['Job_Category'].value_counts()
    location_counts = unique_jobs['Location_Category'].value_counts()
    top_locations = unique_jobs['Location'].value_counts().head(6) if 'Location' in unique_jobs.columns else pd.Series()

    # --- Plotting Setup ---
    plt.style.use('default')
    fig, ax = plt.subplots(figsize=(20, 12))  # Single large plot
    bar_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

    # 5. Job postings by day (Scrape Date based)
    if 'Scrape Date' in df.columns:
        df['Scrape_Datetime'] = pd.to_datetime(df['Scrape Date'], errors='coerce')
        df['Scrape_Day'] = df['Scrape_Datetime'].dt.strftime('%Y-%m-%d')
        df = df.dropna(subset=['Scrape_Day'])

        # Calculate and plot the overall total line
        jobs_by_day_total = df.groupby('Scrape_Day').size().sort_index()
        ax.plot(jobs_by_day_total.index, jobs_by_day_total.values,
                 marker='o', label='Total Postings', linewidth=5, color='#1f77b4')

        ax.set_title('Number of Job Postings by Scrape Date', fontweight='bold', fontsize=20, pad=20)
        ax.set_ylabel('Number of Postings', fontweight='bold', fontsize=16)
        ax.set_xlabel('Date (Scraped)', fontweight='bold', fontsize=16)
        ax.tick_params(axis='x', rotation=45, labelsize=12)
        ax.tick_params(axis='y', labelsize=12)
        ax.grid(True, linestyle='--', alpha=0.7)
    else:
        ax.text(0.5, 0.5, 'Scrape Date column missing', ha='center', va='center', fontsize=20)
        ax.axis('off')


    # Adjust overall figure margins
    plt.tight_layout()

    # --- Save figure ---
    try:
        fig.savefig(output_path, dpi=300, bbox_inches='tight')
        logger.info('Chart saved successfully: %s', output_path)
    except Exception:
        logger.exception('An error occurred while saving the chart to %s', output_path)
        return 4

    if args.show:
        plt.show()

    plt.close(fig)
    return 0


if __name__ == '__main__':
    args = parse_args()
    sys.exit(main(args))