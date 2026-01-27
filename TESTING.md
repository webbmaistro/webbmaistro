# Testing Guide

## Prerequisites for Testing

### 1. System Requirements
- Python 3.8+ installed
- Internet connection
- 1-2 GB free disk space (for Playwright browser)

### 2. Installation Steps
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browser
playwright install chromium
```

### 3. Create Test CSV
Create a file called `restaurants.csv` with 2-3 **safe test websites** first:

```csv
website_url,restaurant_name
https://www.your-own-website.com,Your Test Site
https://www.chipotle.com,Chipotle
https://www.subway.com,Subway
```

**Important**: Start with websites you own or large chains where a test submission won't cause issues.

## Testing Process

### Step 1: Verify Configuration
Check `contact_crawler.py` around line 444 to see your actual message:

```python
config = {
    'sender_name': 'Webb Hammond',
    'sender_email': 'webb@flowdrop.ai',
    'message_template': (
        "Hi [restaurant_name], I'm Webb from Flowdrop. We've built an AI agent "
        "for restaurant back office that's cheaper than MarginEdge and handles "
        "scheduling too. We're filling a small pilot group to test it. Would love "
        "to show you a quick demo: https://calendly.com/webb-flowdrop/new-meeting"
    ),
}
```

### Step 2: Run in Visual Mode
1. Open `contact_crawler.py`
2. Find line ~466: `headless = True`
3. Change to: `headless = False`
4. Save the file

### Step 3: Run Test
```bash
python contact_crawler.py
```

You'll see:
- Browser window open
- Navigation to each website
- Contact page search
- Form filling in real-time
- Submission process

### Step 4: Verify Results
- Check `restaurants_results.csv` for status
- Check `logs/crawler_*.log` for detailed information
- **Check your email** (webb@flowdrop.ai) for:
  - Confirmation emails from websites
  - Bounce-back messages
  - Auto-replies

### Step 5: Review Before Full Run
- Did it find contact pages correctly?
- Did forms fill out properly?
- Did submissions succeed?
- Is the message formatting correct?

## Common Test Issues

### Issue: Can't find contact pages on test sites
- Some large chains hide contact forms
- Try smaller, local restaurant websites
- Look for sites with obvious "Contact Us" pages first

### Issue: Forms not submitting
- Check logs to see what fields were found
- Some forms require phone numbers or other fields
- CAPTCHA will block automation

### Issue: Message looks wrong
- Edit the `message_template` in `contact_crawler.py` (line ~447)
- Make sure [restaurant_name] placeholder is present
- Test with your own website first to see the exact output

## Safe Testing Websites

Best sites to test on:
1. **Your own website** - safest option
2. **Large chain restaurants** - one test message won't hurt
3. **Inactive/demo websites** - test form functionality only

Avoid testing on:
- Small local businesses (until you're ready to actually contact them)
- Sites where you've already reached out manually
- Sites with aggressive CAPTCHA/bot protection

## After Testing

Once verified:
1. Set `headless = True` back in `contact_crawler.py`
2. Create your full `restaurants.csv` with all 1000+ sites
3. Run the full automation: `python contact_crawler.py`
4. Let it run overnight or in the background
5. Monitor the first 10-20 submissions to ensure quality

## Stopping and Resuming

- Press `Ctrl+C` to stop at any time
- Already-processed sites (status = "sent") will be skipped
- Safe to restart anytime
