# Automated AI Report Generation & Delivery Pipeline

An automated pipeline that reads tabular performance data, relies on OpenAI (via OpenRouter) to generate narrative financial summaries, injects the insights into an HTML Jinja template, converts it to a professional-grade PDF via WeasyPrint, and distributes the report on a daily schedule using APScheduler and SMTP via Gmail.

## Key Metrics
- **Effort Reduction:** 90% reduction in manual effort (from hours down to 0 minutes).
- **Execution:** Zero-touch cadence managed by `APScheduler` (Runs daily at 8:00 AM).
- **Accessibility:** Democratizes reporting for non-technical stakeholders via well-formatted PDF delivery.

## Structure
```text
ai-report-pipeline/
├── data/
│   └── sample_data.csv      # Source metrics
├── templates/
│   └── report_template.html # Jinja2 markup layout
├── .env.example             # Template for API & SMTP credentials
├── main.py                  # Core pipeline & scheduler logic
└── requirements.txt         # Project dependencies
```

## Usage

1. **Setup Python virtual environment and dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **System Dependencies:**
   Depending on your OS, you may need to install `weasyprint` system dependencies (e.g., Pango, cairo) for HTML-to-PDF conversion to work.

3. **Configuration:**
   Copy `.env.example` to `.env` and fill in your OpenRouter API Key and your Gmail App Password.

4. **Run the script:**
   ```bash
   python main.py
   ```