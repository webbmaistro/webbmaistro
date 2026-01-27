# Restaurant Contact Form Crawler

Automatically find and submit contact forms on restaurant websites at scale using Python and Playwright.

## Overview

This tool helps you reach out to restaurants by:
- Automatically finding contact pages on restaurant websites
- Detecting and filling out contact forms intelligently
- Submitting personalized messages at scale
- Tracking results and handling errors gracefully

Perfect for B2B outreach, partnership requests, or any legitimate bulk contact needs.

## Features

- **Smart Contact Page Detection**: Tries common URL patterns and searches for contact links
- **Intelligent Form Field Detection**: Automatically identifies name, email, message, and other form fields
- **AI-Powered Fallback**: Optional LLM-based form detection for complex forms (uses Ollama - 100% free, local) - See [LLM_SETUP.md](LLM_SETUP.md)
- **Error Handling**: Gracefully handles failures and continues to the next website
- **Progress Saving**: Saves results after each submission so you never lose progress
- **Rate Limiting**: Built-in random delays (20-40 seconds) to avoid overwhelming servers
- **Detailed Logging**: Comprehensive logs for debugging and tracking
- **Headless Mode**: Can run invisibly in the background after testing
- **Resume Capability**: Skip already-processed websites automatically

## Requirements

- Python 3.8 or higher
- Internet connection

## Installation

### 1. Clone or Download This Repository

```bash
git clone https://github.com/webbmaistro/contactUsCrawler.git
cd contactUsCrawler
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Playwright Browsers

```bash
playwright install chromium
```

This downloads the Chromium browser that Playwright will use for automation.

### 4. Optional: Enable AI-Powered Form Detection (100% Free!)

For better success rates on complex forms, set up Ollama (recommended):

```bash
# Install Ollama (one-time setup)
curl -fsSL https://ollama.com/install.sh | sh

# Download AI model
ollama pull llama3.2

# Install Python SDK
pip install ollama
```

See [LLM_SETUP.md](LLM_SETUP.md) for detailed instructions.

**Cost: $0** - Runs completely locally on your machine. No API fees, ever.

Skip this step to use selector-based detection only (60-70% success rate vs 85-95% with LLM).

## Setup

### 1. Prepare Your CSV File

Create a CSV file named `restaurants.csv` with two columns:
- `website_url`: The restaurant's website URL
- `restaurant_name`: The restaurant's name

Example:

```csv
website_url,restaurant_name
https://www.joes-pizza.com,Joe's Pizza
https://www.marias-bistro.com,Maria's Bistro
https://www.thesushispot.com,The Sushi Spot
```

You can use the `sample_restaurants.csv` file as a template.

### 2. Configure Your Settings

Edit `config.py` to customize:
- Your name and email
- Your message template
- Delay settings
- Input/output file paths

The default configuration is already set up for the Flowdrop outreach campaign.

## Usage

### Basic Usage

Run the crawler with:

```bash
python contact_crawler.py
```

The script will:
1. Read `restaurants.csv`
2. Process each website one by one
3. Save results to `restaurants_results.csv` after each submission
4. Create detailed logs in the `logs/` directory

### Testing Mode

For your first run, it's recommended to test with headless mode OFF so you can see what's happening:

1. Open `contact_crawler.py`
2. Find the line near the bottom: `headless = True`
3. Change it to: `headless = False`
4. Run with a small test CSV (2-3 websites)

```bash
python contact_crawler.py
```

You'll see the browser window open and watch the automation in action.

### Production Mode

Once you've verified it works:
1. Set `headless = True` in `contact_crawler.py`
2. Run with your full CSV file
3. Let it run in the background

The script can be safely interrupted (Ctrl+C) and restarted - it will skip websites that have already been successfully processed.

## Output

### Results CSV

The script creates `restaurants_results.csv` with your original data plus two new columns:

- `contact_page_url`: The URL of the contact page found (if any)
- `status`: One of:
  - `sent`: Successfully submitted
  - `no contact page found`: Couldn't find a contact page
  - `failed: [reason]`: Submission failed with reason
  - `error: [reason]`: An error occurred

### Log Files

Detailed logs are saved to `logs/crawler_YYYYMMDD_HHMMSS.log` with:
- Timestamp for each action
- URLs being processed
- Form fields found
- Success/failure messages
- Error details

## How It Works

### Contact Page Detection

The crawler uses multiple strategies to find contact pages:

1. **URL Pattern Matching**: Tries common patterns like:
   - `/contact`
   - `/contact-us`
   - `/get-in-touch`
   - And more...

2. **Link Text Search**: Scans the homepage for links containing:
   - "Contact"
   - "Contact Us"
   - "Get In Touch"
   - And more...

3. **Form Verification**: Confirms the page has an actual contact form before proceeding

### Form Field Detection

The crawler intelligently identifies form fields using multiple selectors:

- **Name Field**: Looks for inputs with `name`, `id`, or `placeholder` containing "name"
- **Email Field**: Finds email inputs by type, name, or placeholder
- **Message Field**: Locates textareas with relevant identifiers
- **Submit Button**: Identifies submit buttons by type, text, or value

### Form Submission

Once fields are identified:
1. Fills in your information
2. Handles required checkboxes (like privacy policy agreements)
3. Clicks the submit button
4. Waits for confirmation
5. Verifies success by looking for "thank you" messages or URL changes

## Customization

### Modify the Message Template

Edit `config.py`:

```python
MESSAGE_TEMPLATE = (
    "Hi [restaurant_name], your custom message here..."
)
```

The `[restaurant_name]` placeholder will be replaced with the actual restaurant name from your CSV.

### Adjust Delays

To change the delay between submissions (default: 20-40 seconds):

```python
MIN_DELAY_SECONDS = 30
MAX_DELAY_SECONDS = 60
```

### Add Custom Contact Page Patterns

If your target websites use unusual contact page URLs:

```python
CUSTOM_CONTACT_PATTERNS = [
    '/reservations',
    '/inquiries',
    '/book-now',
]
```

## Troubleshooting

### "No contact page found" for many websites

- Some websites hide contact pages behind JavaScript
- Try setting `headless = False` to see what the browser sees
- Some sites use modal dialogs instead of dedicated pages
- Consider manually finding contact pages for important targets

### Forms not submitting

- Check logs to see which form fields were found
- Some forms use CAPTCHA or bot protection
- Some forms require additional fields not detected automatically
- Run in non-headless mode to watch what happens

### "Timeout" errors

- Increase the `TIMEOUT` value in `config.py`
- Some websites are slow to load
- Check your internet connection

### Import errors

Make sure you've installed all dependencies:

```bash
pip install -r requirements.txt
playwright install chromium
```

### Browser not found

Run:

```bash
playwright install chromium
```

## Best Practices

1. **Start Small**: Test with 5-10 websites first
2. **Check Logs**: Review the logs to see what's working and what's not
3. **Respect Rate Limits**: Keep delays at 20+ seconds
4. **Monitor Results**: Check your email for bounce-backs or responses
5. **Be Ethical**: Only use for legitimate business outreach
6. **Stay Compliant**: Ensure your outreach complies with anti-spam laws (CAN-SPAM, GDPR, etc.)

## Performance

- Processes approximately 60-90 websites per hour (with 20-40 second delays)
- 1000 websites will take roughly 12-18 hours
- Can run overnight or in the background
- Resumable if interrupted

## Limitations

- Cannot bypass CAPTCHAs
- May not work on JavaScript-heavy single-page applications
- Some websites use modal contact forms instead of dedicated pages
- Rate limiting and timeouts can slow down processing
- Success rate varies by website (typically 60-80%)

## Security & Privacy

- No data is sent to external services except the target websites
- Your credentials are only in the config file (never share this publicly)
- Logs contain URLs and form field names (but not passwords)
- Uses a realistic browser user agent to avoid being blocked

## Legal Notice

This tool is intended for legitimate business outreach only. You are responsible for:
- Complying with anti-spam laws (CAN-SPAM Act, GDPR, etc.)
- Respecting website terms of service
- Obtaining necessary consent for data processing
- Following up on opt-out requests

The authors assume no liability for misuse of this tool.

## Support

For issues, questions, or contributions:
- Open an issue on GitHub: https://github.com/webbmaistro/contactUsCrawler/issues
- Email: webb@flowdrop.ai

## License

MIT License - feel free to use and modify for your needs.

## Changelog

### Version 1.0.0 (2026-01-27)
- Initial release
- Contact page detection with multiple strategies
- Intelligent form field detection
- Automatic form submission
- Progress saving and resume capability
- Comprehensive logging
- Rate limiting with random delays

---

Built with ❤️ by Webb Hammond for the restaurant tech community
