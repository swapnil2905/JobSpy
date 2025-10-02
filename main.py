import csv
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import pandas as pd
from jobspy import scrape_jobs

try:
    jobs = scrape_jobs(
        site_name=["indeed", "linkedin", "zip_recruiter", "google"], # "glassdoor", "bayt", "naukri", "bdjobs"
        search_term="  Accountant",
        google_search_term="  Accountant jobs near Melbourne, VIC since this week",
        location="Melbourne , VIC",
        results_wanted=15,
        hours_old=4,
        country_indeed='AUSTRALIA',
        
        # linkedin_fetch_description=True # gets more info such as description, direct job url (slower)
        #proxies=["208.195.175.46:65095", "208.195.175.45:65095", "localhost"],
    )
    print(f"Found {len(jobs)} jobs")
    print(jobs.head())
    jobs.to_csv("jobs.csv", quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False) # to_excel
except Exception as e:
    print(f"Error during job scraping: {e}")
    import traceback
    traceback.print_exc()
    # Create empty DataFrame for HTML generation
    jobs = pd.DataFrame()

# Generate HTML for web display
try:
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Latest Job Scraping Results</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <header>
        <h1>Latest Job Scraping Results</h1>
        <p>Updated on {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
    </header>
    <main>
        <p>Found {len(jobs)} jobs</p>
        {jobs.to_html(index=False, classes='jobs-table') if not jobs.empty else '<p>No jobs found.</p>'}
    </main>
    <footer>
        <p>Powered by JobSpy</p>
    </footer>
</body>
</html>
"""

    with open("portfolio/jobs.html", "w") as f:
        f.write(html_content)
    print("HTML file generated successfully.")
except Exception as e:
    print(f"Error generating HTML: {e}")
    import traceback
    traceback.print_exc()

# Send results via email if configured
sender_email = os.getenv('SENDER_EMAIL')
sender_password = os.getenv('SENDER_PASSWORD')
receiver_email = os.getenv('RECEIVER_EMAIL')

if sender_email and sender_password and receiver_email:
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = 'Job Scraper Results'

        html_table = jobs.head().to_html()
        body = f"<p>Found {len(jobs)} jobs</p>{html_table}"
        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
        print("Results sent via email.")
    except Exception as e:
        print(f"Failed to send email: {e}")
