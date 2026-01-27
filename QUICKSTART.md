# Quick Start Guide

Get up and running with the Contact Form Crawler in 5 minutes.

## Prerequisites

- Python 3.8+ installed
- Internet connection

## Installation (2 minutes)

```bash
# 1. Clone the repository
git clone https://github.com/webbmaistro/contactUsCrawler.git
cd contactUsCrawler

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install Playwright browser
playwright install chromium
```

## Setup (2 minutes)

### 1. Create Your CSV File

Create a file named `restaurants.csv` with this format:

```csv
website_url,restaurant_name
https://www.restaurant1.com,Restaurant Name 1
https://www.restaurant2.com,Restaurant Name 2
```

You can copy `sample_restaurants.csv` and replace with your actual data.

### 2. Customize Your Message (Optional)

Edit `config.py` to change:
- Your name (`SENDER_NAME`)
- Your email (`SENDER_EMAIL`)
- Your message template (`MESSAGE_TEMPLATE`)

## Run (1 minute)

### First Test Run (with visible browser)

Edit `contact_crawler.py` and change line ~466:
```python
headless = False  # Change True to False
```

Then run:
```bash
python contact_crawler.py
```

You'll see the browser window and watch it work on 2-3 test sites.

### Production Run (headless)

Once you've verified it works:

1. Change `headless = False` back to `headless = True` in `contact_crawler.py`
2. Update `restaurants.csv` with your full list
3. Run:

```bash
python contact_crawler.py
```

The script will:
- Process websites one by one
- Save progress to `restaurants_results.csv` after each submission
- Create logs in `logs/` directory
- Take 20-40 seconds between each submission

## Check Results

Open `restaurants_results.csv` to see:
- Which forms were successfully submitted
- Contact page URLs found
- Any errors or issues

Check `logs/crawler_*.log` for detailed information.

## Interrupt and Resume

You can safely stop the script (Ctrl+C) and restart it. It will automatically skip websites that were already successfully processed.

## Common Issues

**"No module named 'playwright'"**
```bash
pip install -r requirements.txt
```

**"Browser not found"**
```bash
playwright install chromium
```

**"No contact page found" for many sites**
- Normal! Success rate is typically 60-80%
- Check logs to see what's happening
- Try running with `headless = False` to debug

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Customize contact page patterns in `config.py`
- Adjust delays if needed
- Monitor your email for responses

## Support

Issues? Questions?
- GitHub: https://github.com/webbmaistro/contactUsCrawler/issues
- Email: webb@flowdrop.ai

Good luck with your outreach!
