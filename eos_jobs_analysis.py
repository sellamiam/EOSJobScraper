import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sqlite3



# --- File Paths ---
csv_file_path = '/Users/msellamia/Scripts/EOSJobScraper/eos_jobs.csv'
db_file_path = '/Users/msellamia/Scripts/EOSJobScraper/eos_jobs.db'
output_path = '/Users/msellamia/Scripts/EOSJobScraper/eos_jobs_analysis.png'


# --- Load CSV ---
try:
    df = pd.read_csv(csv_file_path)
except FileNotFoundError:
    print(f"Error: The file {csv_file_path} was not found. Please ensure it is in the correct directory.")
    exit()

# --- Data Cleaning ---
def categorize_location(loc):
    """Categorizes job location into broader regions."""
    if 'PA' in str(loc):
        return 'PA'
    elif 'NJ' in str(loc):
        return 'NJ'
    elif 'Remote' in str(loc):
        return 'Remote'
    elif 'TX' in str(loc):
        return 'TX'
    elif 'CA' in str(loc):
        return 'CA'
    elif 'Locations' in str(loc):
        return 'Multiple'
    else:
        return 'Other'

# Use .loc to avoid SettingWithCopyWarning
df.loc[:, 'Location_Category'] = df['Location'].apply(categorize_location)
unique_jobs = df.drop_duplicates(subset=['Title', 'Location'])

# --- Categorize jobs ---
def categorize_job(title):
    """Categorizes job title into job families."""
    t = title.lower()
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

# Apply job categorization to both the full DataFrame and unique_jobs DataFrame
unique_jobs.loc[:, 'Job_Category'] = unique_jobs['Title'].apply(categorize_job)
df.loc[:, 'Job_Category'] = df['Title'].apply(categorize_job)

# --- Counts ---
job_category_counts = unique_jobs['Job_Category'].value_counts()
location_counts = unique_jobs['Location_Category'].value_counts()
top_locations = unique_jobs['Location'].value_counts().head(6)

# --- Plotting Setup ---
plt.style.use('default')
fig, axes = plt.subplots(2, 3, figsize=(26, 10))
pie_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#8c564b', '#d62728', '#9467bd', '#7f7f7f'][:len(location_counts)]
bar_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

# 1. Overall Job Types
axes[0, 0].bar(job_category_counts.index, job_category_counts.values, color=bar_colors)
axes[0, 0].set_title('Overall Job Type Distribution', fontweight='bold', fontsize=12)
axes[0, 0].set_ylabel('Number of Positions', fontweight='bold', fontsize=11)
axes[0, 0].tick_params(axis='x', rotation=30, labelsize=10)

# 2. Geographic Distribution by Category
axes[0, 1].bar(location_counts.index, location_counts.values, color=pie_colors)
axes[0, 1].set_title('Job Postings by Location Category', fontweight='bold', fontsize=12)
axes[0, 1].set_ylabel('Number of Positions', fontweight='bold', fontsize=11)
axes[0, 1].tick_params(axis='x', rotation=30, labelsize=10)

# 3. Pie chart for locations
axes[0, 2].pie(location_counts.values, labels=location_counts.index, colors=pie_colors, autopct='%1.1f%%', startangle=90, textprops={'fontsize': 10})
axes[0, 2].set_title('Geographic Distribution (%)', fontweight='bold', fontsize=12)

# 4. Top Specific Locations
axes[1, 0].bar(top_locations.index, top_locations.values, color=bar_colors[:len(top_locations)])
axes[1, 0].set_title('Top 6 Specific Locations', fontweight='bold', fontsize=12)
axes[1, 0].set_ylabel('Number of Positions', fontweight='bold', fontsize=11)
axes[1, 0].tick_params(axis='x', rotation=30, labelsize=10)

# 5. Job postings by day & category (UPDATED to include overall)
if 'Scrape Date' in df.columns:
    df['Scrape_Day'] = pd.to_datetime(df['Scrape Date']).dt.strftime('%Y-%m-%d')
    
    jobs_by_day_category = df.groupby(['Scrape_Day', 'Job_Category']).size().unstack(fill_value=0)
    
    # Plot each job category as a separate line
    for i, column in enumerate(jobs_by_day_category.columns):
        axes[1, 1].plot(jobs_by_day_category.index, jobs_by_day_category[column], 
                         marker='o', label=column, linewidth=2, color=bar_colors[i % len(bar_colors)])

    # Calculate and plot the overall total line
    jobs_by_day_total = df.groupby('Scrape_Day').size()
    axes[1, 1].plot(jobs_by_day_total.index, jobs_by_day_total.values, 
                     marker='o', label='Overall Total', linewidth=4, color='black', linestyle='--')
    
    axes[1, 1].set_title('Number of Job Postings by Day & Category', fontweight='bold', fontsize=12)
    axes[1, 1].set_ylabel('Number of Postings', fontweight='bold', fontsize=11)
    axes[1, 1].set_xlabel('Date', fontweight='bold', fontsize=11)
    axes[1, 1].tick_params(axis='x', rotation=30, labelsize=10)
    axes[1, 1].legend(title='Job Category', fontsize=9, bbox_to_anchor=(1.05, 1), loc='upper left')
else:
    axes[1, 1].axis('off')

# 6. Recent jobs table (last 7 days)
try:
    conn = sqlite3.connect(db_file_path)
    c = conn.cursor()
    c.execute('''
        SELECT title, location, date(scrape_date) as job_post_date
        FROM jobs
        WHERE DATE(scrape_date) > DATE('now', '-7 day')
          AND title IS NOT NULL 
          AND title != ''
    ''')
    recent_jobs = c.fetchall()
    conn.close()

    if recent_jobs:
        table_data = recent_jobs[:15]
        col_labels = ['Title', 'Location', 'Job Post Date']
        axes[1, 2].axis('off')
        
        table = axes[1, 2].table(cellText=table_data, colLabels=col_labels,
                                loc='center', cellLoc='left', colLoc='left')
        
        table.auto_set_font_size(False)
        table.set_fontsize(11)
        table.scale(1, 1.5)
        for i, width in enumerate([0.65, 0.25, 0.25]):
            for key, cell in table.get_celld().items():
                if key[1] == i:
                    cell.set_width(width)
        
        axes[1, 2].set_title('Recent Job Postings (Last 7 Days, sample 15)',
                            fontweight='bold', fontsize=12, pad=40)
    else:
        axes[1, 2].text(0.5, 0.5, 'No recent job postings', ha='center', va='center', fontsize=14)
        axes[1, 2].axis('off')

except sqlite3.OperationalError:
    print(f"Error: The database file {db_file_path} was not found or is corrupted.")
    axes[1, 2].text(0.5, 0.5, 'DB Error: No recent postings table', ha='center', va='center', fontsize=12, color='red')
    axes[1, 2].axis('off')

# Adjust overall figure margins
plt.tight_layout(h_pad=3, w_pad=2)
plt.subplots_adjust(top=0.92)

# --- Save figure ---
try:
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Chart saved successfully: {output_path}")
except Exception as e:
    print(f"An error occurred while saving the chart: {e}")

plt.close()