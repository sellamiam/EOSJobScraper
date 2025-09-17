import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Load CSV
df = pd.read_csv('/Users/msellamia/Downloads/EOS_Jobs.csv')

# --- Data cleaning ---
def categorize_location(loc):
    if 'PA' in loc:
        return 'PA'
    elif 'NJ' in loc:
        return 'NJ'
    elif 'Remote' in loc:
        return 'Remote'
    elif 'TX' in loc:
        return 'TX'
    elif 'CA' in loc:
        return 'CA'
    elif 'Locations' in str(loc):
        return 'Multiple'
    else:
        return 'Other'

df['Location_Category'] = df['Location'].apply(categorize_location)
unique_jobs = df.drop_duplicates(subset=['Title', 'Location'])

# --- Categorize jobs ---
def categorize_job(title):
    t = title.lower()
    if any(w in t for w in ['engineer', 'technician', 'designer']):
        return 'Engineering/Technical'
    elif any(w in t for w in ['manager', 'supervisor', 'lead', 'director']):
        return 'Management'
    elif any(w in t for w in ['analyst', 'specialist', 'coordinator', 'administrator']):
        return 'Operations/Support'
    elif any(w in t for w in ['intern', 'temporary']):
        return 'Internship/Temporary'
    else:
        return 'Other'

unique_jobs['Job_Category'] = unique_jobs['Title'].apply(categorize_job)

# --- Counts ---
job_category_counts = unique_jobs['Job_Category'].value_counts()
location_counts = unique_jobs['Location_Category'].value_counts()
top_locations = unique_jobs['Location'].value_counts().head(6)

# --- Job postings by day ---
# Ensure 'Scrape Date' exists, split if contains time
if 'Scrape Date' in df.columns:
    df['Scrape_Day'] = df['Scrape Date'].str.split().str[0]
    jobs_by_day = df['Scrape_Day'].value_counts().sort_index()
else:
    jobs_by_day = pd.Series(dtype=int)

# Pie chart colors
pie_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#8c564b', '#d62728', '#9467bd', '#7f7f7f'][:len(location_counts)]

# --- Plot ---
plt.style.use('default')
fig, axes = plt.subplots(2, 3, figsize=(18, 10))  # 2 rows x 3 columns

# 1. Overall Job Types
axes[0,0].bar(job_category_counts.index, job_category_counts.values, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'])
axes[0,0].set_title('Overall Job Type Distribution', fontweight='bold', fontsize=12)
axes[0,0].set_ylabel('Number of Positions', fontweight='bold', fontsize=11)
axes[0,0].tick_params(axis='x', rotation=30, labelsize=10)

# 2. Geographic Distribution by Category
axes[0,1].bar(location_counts.index, location_counts.values, color=pie_colors)
axes[0,1].set_title('Job Postings by Location Category', fontweight='bold', fontsize=12)
axes[0,1].set_ylabel('Number of Positions', fontweight='bold', fontsize=11)
axes[0,1].tick_params(axis='x', rotation=30, labelsize=10)

# 3. Pie chart for locations
axes[0,2].pie(location_counts.values, labels=location_counts.index, colors=pie_colors, autopct='%1.1f%%', startangle=90, textprops={'fontsize': 10})
axes[0,2].set_title('Geographic Distribution (%)', fontweight='bold', fontsize=12)

# 4. Top Specific Locations
axes[1,0].bar(top_locations.index, top_locations.values, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#8c564b', '#d62728', '#9467bd'])
axes[1,0].set_title('Top 6 Specific Locations', fontweight='bold', fontsize=12)
axes[1,0].set_ylabel('Number of Positions', fontweight='bold', fontsize=11)
axes[1,0].tick_params(axis='x', rotation=30, labelsize=10)

# 5. Job postings by day
if not jobs_by_day.empty:
    axes[1,1].bar(jobs_by_day.index, jobs_by_day.values, color='#2ca02c')
    axes[1,1].set_title('Number of Job Postings by Day', fontweight='bold', fontsize=12)
    axes[1,1].set_ylabel('Number of Postings', fontweight='bold', fontsize=11)
    axes[1,1].tick_params(axis='x', rotation=30, labelsize=10)
else:
    axes[1,1].axis('off')

# 6. Empty placeholder
axes[1,2].axis('off')

plt.tight_layout(h_pad=3, w_pad=2)
plt.subplots_adjust(top=0.92)

# --- Save figure ---
output_path = '/Users/msellamia/Scripts/EOSJobScraper/eos_jobs_analysis.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
plt.close()

print(f"Chart saved successfully: {output_path}")
