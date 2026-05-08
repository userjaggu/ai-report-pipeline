import os
import smtplib
import pandas as pd
from email.message import EmailMessage
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from apscheduler.schedulers.blocking import BlockingScheduler

# Load environment variables
load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "465"))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD") # App password recommended for Gmail
EMAIL_TO = os.getenv("EMAIL_TO")

def read_data(filepath):
    """1. Reads the CSV file and returns a pandas DataFrame."""
    print(f"Reading data from {filepath}...")
    df = pd.read_csv(filepath)
    return df

def generate_commentary(df):
    """2. Uses OpenAI API to generate a 3-paragraph summary."""
    print("Generating AI commentary...")
    if not OPENAI_API_KEY or OPENAI_API_KEY == 'your_openai_api_key_here':
        print("Warning: OPENAI_API_KEY not configured. Returning placeholder.")
        return "<p>API Key not configured. Paragraph 1.</p><p>Paragraph 2.</p><p>Paragraph 3.</p>"
        
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENAI_API_KEY,
    )
    
    # Summarize data to feed to the prompt
    summary_stats = df.groupby('category')['value'].agg(['mean', 'sum', 'count']).to_string()
    
    prompt = f"""You are a financial analyst assistant. Given the following data summary:

{summary_stats}

Write a concise 3-paragraph professional commentary:
- Paragraph 1: Overall performance snapshot with key numbers
- Paragraph 2: Notable trends or anomalies
- Paragraph 3: Forward-looking observation

Be factual, professional, and under 200 words. Do not hallucinate numbers not present in the data.
Format your output strictly as HTML paragraphs (<p>text</p>)."""

    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-3-8b-instruct:free", # Using a free model on OpenRouter!
            max_tokens=300,
            messages=[
                {"role": "system", "content": "You are a professional financial analyst."},
                {"role": "user", "content": prompt}
            ]
        )
        # Assuming the response returns HTML string directly since instructed 
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return "<p>Error generating AI commentary.</p>"

def format_report(df, commentary, template_dir="templates", template_name="report_template.html"):
    """3. Injects commentary and data into Jinja2 template and renders HTML."""
    print("Rendering HTML report...")
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(template_name)
    
    # Convert dataframe to HTML table
    html_table = df.to_html(index=False, border=0, classes="dataframe")
    
    # Current date
    report_date = datetime.now().strftime("%Y-%m-%d")
    
    rendered_html = template.render(
        date=report_date,
        commentary=commentary,
        data_table=html_table
    )
    return rendered_html

def generate_pdf(html_content, output_path="report.pdf"):
    """4. Converts HTML to PDF using WeasyPrint."""
    print(f"Generating PDF at {output_path}...")
    HTML(string=html_content).write_pdf(output_path)
    return output_path

def send_email(pdf_path):
    """5. Sends the generated PDF via email."""
    if not EMAIL_USER or not EMAIL_PASSWORD or EMAIL_USER == 'your_email@gmail.com':
        print("Email credentials missing or placeholder. Skipping email send.")
        return

    print(f"Sending email from {EMAIL_USER} to {EMAIL_TO}...")
    msg = EmailMessage()
    msg['Subject'] = f"Daily Performance Report - {datetime.now().strftime('%Y-%m-%d')}"
    msg['From'] = EMAIL_USER
    msg['To'] = EMAIL_TO
    msg.set_content("Please find attached your automated daily performance report.")

    # Attach PDF
    with open(pdf_path, 'rb') as f:
        pdf_data = f.read()
        msg.add_attachment(pdf_data, maintype='application', subtype='pdf', filename="Daily_Performance_Report.pdf")

    # Send via SMTP
    try:
        with smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT) as server:
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

def job():
    """Main pipeline execution."""
    print(f"\\n--- Starting Report Pipeline Job at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
    
    data_file = "data/sample_data.csv"
    
    # Step 1: Read Data
    df = read_data(data_file)
    
    # Step 2: Generate Commentary via OpenAI
    commentary = generate_commentary(df)
    
    # Step 3: Format Report Template
    html_report = format_report(df, commentary)
    
    # Step 4: Render PDF
    pdf_path = generate_pdf(html_report)
    
    # Step 5: Email the report
    send_email(pdf_path)
    
    print("--- Job Finished ---\\n")

if __name__ == "__main__":
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    os.makedirs("templates", exist_ok=True)
    
    # Run once at startup
    print("Running initial test execution...")
    job()
    
    # Step 6: Schedule automatically every day at 8 AM
    print("Setting up APScheduler for 8:00 AM daily runs...")
    scheduler = BlockingScheduler()
    scheduler.add_job(job, 'cron', hour=8, minute=0)
    
    try:
        print("Scheduler is running. Press Ctrl+C to exit.")
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("Scheduler stopped.")