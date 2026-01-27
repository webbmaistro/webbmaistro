#!/usr/bin/env python3
"""
Contact Form Crawler
Automatically finds and submits contact forms on restaurant websites.
"""

import asyncio
import csv
import json
import logging
import os
import random
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

import pandas as pd
from playwright.async_api import Page, TimeoutError, async_playwright

# Optional: Import Anthropic SDK for LLM-powered form detection
try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class ContactFormCrawler:
    """Crawler for finding and submitting contact forms on websites."""

    # Common contact page URL patterns
    CONTACT_PATTERNS = [
        '/contact',
        '/contact-us',
        '/contactus',
        '/contact_us',
        '/get-in-touch',
        '/reach-out',
        '/reach-us',
        '/contact-form',
        '/support',
        '/help',
        '/feedback',
    ]

    # Common link text patterns for contact pages
    CONTACT_LINK_TEXT = [
        'contact',
        'contact us',
        'get in touch',
        'reach out',
        'reach us',
        'talk to us',
        'message us',
        'email us',
        'support',
        'feedback',
    ]

    # Common form field selectors
    FIELD_SELECTORS = {
        'name': [
            'input[name*="name"]:not([name*="last"]):not([name*="sur"])',
            'input[id*="name"]:not([id*="last"]):not([id*="sur"])',
            'input[placeholder*="name" i]:not([placeholder*="last" i])',
            'input[type="text"]:first-of-type',
        ],
        'email': [
            'input[name*="email" i]',
            'input[id*="email" i]',
            'input[type="email"]',
            'input[placeholder*="email" i]',
        ],
        'message': [
            'textarea[name*="message" i]',
            'textarea[id*="message" i]',
            'textarea[name*="comment" i]',
            'textarea[id*="comment" i]',
            'textarea[placeholder*="message" i]',
            'textarea:first-of-type',
        ],
        'phone': [
            'input[name*="phone" i]',
            'input[id*="phone" i]',
            'input[type="tel"]',
            'input[placeholder*="phone" i]',
        ],
    }

    def __init__(self, config: Dict):
        """Initialize the crawler with configuration."""
        self.config = config
        self.setup_logging()

    def setup_logging(self):
        """Setup logging configuration."""
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = log_dir / f'crawler_{timestamp}.log'

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Logging initialized. Log file: {log_file}")

    async def find_contact_page(self, page: Page, base_url: str) -> Optional[str]:
        """
        Find the contact page URL for a given website.

        Args:
            page: Playwright page object
            base_url: Base URL of the website

        Returns:
            Contact page URL if found, None otherwise
        """
        self.logger.info(f"Searching for contact page on {base_url}")

        try:
            # First, try common URL patterns
            for pattern in self.CONTACT_PATTERNS:
                potential_url = urljoin(base_url, pattern)
                try:
                    response = await page.goto(potential_url, wait_until='networkidle', timeout=10000)
                    if response and response.ok:
                        # Check if page has a form
                        forms = await page.locator('form').count()
                        if forms > 0:
                            self.logger.info(f"Found contact page via pattern: {potential_url}")
                            return potential_url
                except Exception:
                    continue

            # If patterns don't work, go to homepage and look for contact links
            await page.goto(base_url, wait_until='networkidle', timeout=15000)
            await page.wait_for_timeout(2000)  # Wait for dynamic content

            # Look for links with contact-related text
            all_links = await page.locator('a').all()

            for link in all_links:
                try:
                    text = await link.inner_text()
                    href = await link.get_attribute('href')

                    if not text or not href:
                        continue

                    text_lower = text.lower().strip()

                    # Check if link text matches contact patterns
                    if any(pattern in text_lower for pattern in self.CONTACT_LINK_TEXT):
                        contact_url = urljoin(base_url, href)

                        # Verify it's a valid URL from the same domain
                        if self._is_same_domain(base_url, contact_url):
                            # Visit the link to verify it has a form
                            try:
                                await page.goto(contact_url, wait_until='networkidle', timeout=10000)
                                forms = await page.locator('form').count()
                                if forms > 0:
                                    self.logger.info(f"Found contact page via link: {contact_url}")
                                    return contact_url
                            except Exception:
                                continue

                except Exception:
                    continue

            self.logger.warning(f"No contact page found for {base_url}")
            return None

        except Exception as e:
            self.logger.error(f"Error finding contact page for {base_url}: {str(e)}")
            return None

    def _is_same_domain(self, base_url: str, check_url: str) -> bool:
        """Check if two URLs are from the same domain."""
        base_domain = urlparse(base_url).netloc
        check_domain = urlparse(check_url).netloc
        return base_domain == check_domain or check_domain.endswith(f'.{base_domain}')

    async def find_form_field(self, page: Page, field_type: str) -> Optional[str]:
        """
        Find a form field by trying multiple selectors.

        Args:
            page: Playwright page object
            field_type: Type of field (name, email, message, phone)

        Returns:
            Selector for the field if found, None otherwise
        """
        if field_type not in self.FIELD_SELECTORS:
            return None

        for selector in self.FIELD_SELECTORS[field_type]:
            try:
                element = page.locator(selector).first
                if await element.count() > 0 and await element.is_visible():
                    return selector
            except Exception:
                continue

        return None

    async def detect_form_fields_with_llm(self, page: Page) -> Optional[Dict[str, str]]:
        """
        Use LLM to intelligently detect form field selectors.

        Args:
            page: Playwright page object

        Returns:
            Dictionary mapping field types to selectors, or None if LLM unavailable
        """
        if not self.config.get('use_llm_detection', False):
            return None

        if not ANTHROPIC_AVAILABLE:
            self.logger.warning("Anthropic SDK not installed. Install with: pip install anthropic")
            return None

        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            self.logger.warning("ANTHROPIC_API_KEY not set. Skipping LLM detection.")
            return None

        try:
            # Get page HTML (limit to forms to reduce token usage)
            forms_html = await page.locator('form').first.inner_html()

            # Truncate if too long
            if len(forms_html) > 15000:
                forms_html = forms_html[:15000] + "\n... (truncated)"

            self.logger.info("Using LLM to detect form fields...")

            client = Anthropic(api_key=api_key)

            response = client.messages.create(
                model="claude-3-5-haiku-20241022",  # Fast and cheap
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": f"""Analyze this HTML contact form and identify the CSS selectors for each field.

HTML:
{forms_html}

Return ONLY a JSON object with these keys (use null if field not found):
{{
  "name": "css selector for name field",
  "email": "css selector for email field",
  "message": "css selector for message/comment textarea",
  "phone": "css selector for phone field",
  "submit": "css selector for submit button"
}}

Rules:
- Use the most specific selector (prefer [name="..."] or #id)
- For name, avoid last name fields
- Message field is usually a textarea
- Return ONLY the JSON, no explanation"""
                }]
            )

            # Parse response
            response_text = response.content[0].text.strip()

            # Extract JSON if wrapped in markdown code blocks
            if "```" in response_text:
                response_text = re.search(r'```(?:json)?\s*(\{.*\})\s*```', response_text, re.DOTALL)
                if response_text:
                    response_text = response_text.group(1)

            selectors = json.loads(response_text)

            # Filter out null values
            selectors = {k: v for k, v in selectors.items() if v}

            self.logger.info(f"LLM detected fields: {list(selectors.keys())}")
            return selectors

        except Exception as e:
            self.logger.error(f"LLM detection failed: {str(e)}")
            return None

    async def fill_and_submit_form(
        self,
        page: Page,
        contact_url: str,
        name: str,
        email: str,
        message: str
    ) -> Tuple[bool, str]:
        """
        Fill out and submit a contact form.

        Args:
            page: Playwright page object
            contact_url: URL of the contact page
            name: Name to fill in
            email: Email to fill in
            message: Message to fill in

        Returns:
            Tuple of (success: bool, status_message: str)
        """
        try:
            # Navigate to contact page
            await page.goto(contact_url, wait_until='networkidle', timeout=15000)
            await page.wait_for_timeout(2000)

            # Find form fields using selectors
            name_selector = await self.find_form_field(page, 'name')
            email_selector = await self.find_form_field(page, 'email')
            message_selector = await self.find_form_field(page, 'message')
            submit_selector = None

            # If required fields not found, try LLM detection
            if (not email_selector or not message_selector) and self.config.get('use_llm_detection', False):
                self.logger.info("Selector-based detection failed, trying LLM...")
                llm_selectors = await self.detect_form_fields_with_llm(page)

                if llm_selectors:
                    # Override with LLM-detected selectors
                    name_selector = llm_selectors.get('name') or name_selector
                    email_selector = llm_selectors.get('email') or email_selector
                    message_selector = llm_selectors.get('message') or message_selector
                    submit_selector = llm_selectors.get('submit')

            # Check if we have required fields
            if not email_selector or not message_selector:
                return False, "Could not find required form fields (email and message)"

            self.logger.info("Found form fields, filling out form...")

            # Fill name field if it exists
            if name_selector:
                await page.locator(name_selector).first.fill(name)
                self.logger.info("Filled name field")

            # Fill email field (required)
            await page.locator(email_selector).first.fill(email)
            self.logger.info("Filled email field")

            # Fill message field (required)
            await page.locator(message_selector).first.fill(message)
            self.logger.info("Filled message field")

            # Optional: Fill phone field if it exists and is required
            phone_selector = await self.find_form_field(page, 'phone')
            if phone_selector:
                try:
                    phone_field = page.locator(phone_selector).first
                    is_required = await phone_field.get_attribute('required')
                    if is_required:
                        await phone_field.fill('555-123-4567')
                        self.logger.info("Filled phone field (required)")
                except Exception:
                    pass

            # Handle any checkboxes (like privacy policy agreements)
            try:
                checkboxes = await page.locator('input[type="checkbox"][required]').all()
                for checkbox in checkboxes:
                    if await checkbox.is_visible():
                        await checkbox.check()
                        self.logger.info("Checked required checkbox")
            except Exception:
                pass

            # Find and click submit button
            submit_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("submit")',
                'button:has-text("send")',
                'input[value*="submit" i]',
                'input[value*="send" i]',
            ]

            # Prioritize LLM-detected submit selector
            if submit_selector:
                submit_selectors.insert(0, submit_selector)

            submit_clicked = False
            for selector in submit_selectors:
                try:
                    submit_btn = page.locator(selector).first
                    if await submit_btn.count() > 0 and await submit_btn.is_visible():
                        await submit_btn.click()
                        submit_clicked = True
                        self.logger.info(f"Clicked submit button: {selector}")
                        break
                except Exception:
                    continue

            if not submit_clicked:
                return False, "Could not find submit button"

            # Wait for submission to complete
            await page.wait_for_timeout(3000)

            # Check for success indicators
            success_indicators = [
                'thank you',
                'thanks',
                'success',
                'received',
                'submitted',
                'we\'ll be in touch',
                'message sent',
            ]

            page_content = await page.content()
            page_content_lower = page_content.lower()

            if any(indicator in page_content_lower for indicator in success_indicators):
                self.logger.info("Form submission successful")
                return True, "sent"
            else:
                # Check if we're still on the same page (might indicate error)
                current_url = page.url
                if current_url == contact_url:
                    self.logger.warning("Still on contact page after submit, might have failed")
                    return False, "Submission uncertain - no success message detected"
                else:
                    # URL changed, likely successful
                    self.logger.info("Form submission likely successful (URL changed)")
                    return True, "sent"

        except TimeoutError:
            return False, "Timeout while loading contact page"
        except Exception as e:
            self.logger.error(f"Error filling/submitting form: {str(e)}")
            return False, f"Error: {str(e)}"

    async def process_website(
        self,
        page: Page,
        website_url: str,
        restaurant_name: str
    ) -> Dict[str, str]:
        """
        Process a single website: find contact page and submit form.

        Args:
            page: Playwright page object
            website_url: URL of the restaurant website
            restaurant_name: Name of the restaurant

        Returns:
            Dictionary with contact_page_url and status
        """
        result = {
            'contact_page_url': '',
            'status': ''
        }

        try:
            # Ensure URL has protocol
            if not website_url.startswith(('http://', 'https://')):
                website_url = f'https://{website_url}'

            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"Processing: {restaurant_name} - {website_url}")
            self.logger.info(f"{'='*60}")

            # Find contact page
            contact_url = await self.find_contact_page(page, website_url)

            if not contact_url:
                result['status'] = 'no contact page found'
                self.logger.warning(f"No contact page found for {restaurant_name}")
                return result

            result['contact_page_url'] = contact_url

            # Prepare message with restaurant name
            message = self.config['message_template'].replace('[restaurant_name]', restaurant_name)

            # Fill and submit form
            success, status = await self.fill_and_submit_form(
                page,
                contact_url,
                self.config['sender_name'],
                self.config['sender_email'],
                message
            )

            if success:
                result['status'] = status
                self.logger.info(f"✓ Successfully submitted form for {restaurant_name}")
            else:
                result['status'] = f'failed: {status}'
                self.logger.error(f"✗ Failed to submit form for {restaurant_name}: {status}")

        except Exception as e:
            result['status'] = f'error: {str(e)}'
            self.logger.error(f"✗ Error processing {restaurant_name}: {str(e)}")

        return result

    async def run(self, input_csv: str, output_csv: str, headless: bool = True):
        """
        Run the crawler on all websites in the input CSV.

        Args:
            input_csv: Path to input CSV file
            output_csv: Path to output CSV file
            headless: Whether to run browser in headless mode
        """
        # Load input CSV
        try:
            df = pd.read_csv(input_csv)
            self.logger.info(f"Loaded {len(df)} websites from {input_csv}")
        except Exception as e:
            self.logger.error(f"Error loading CSV: {e}")
            return

        # Add result columns if they don't exist
        if 'contact_page_url' not in df.columns:
            df['contact_page_url'] = ''
        if 'status' not in df.columns:
            df['status'] = ''

        # Start Playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=headless)
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            page = await context.new_page()

            # Process each website
            for idx, row in df.iterrows():
                # Skip if already processed successfully
                if row['status'] == 'sent':
                    self.logger.info(f"Skipping {row['restaurant_name']} (already sent)")
                    continue

                website_url = row['website_url']
                restaurant_name = row['restaurant_name']

                # Process website
                result = await self.process_website(page, website_url, restaurant_name)

                # Update dataframe
                df.at[idx, 'contact_page_url'] = result['contact_page_url']
                df.at[idx, 'status'] = result['status']

                # Save progress after each website
                df.to_csv(output_csv, index=False)
                self.logger.info(f"Progress saved to {output_csv}")

                # Random delay between submissions
                if idx < len(df) - 1:  # Don't delay after last item
                    delay = random.randint(
                        self.config['min_delay_seconds'],
                        self.config['max_delay_seconds']
                    )
                    self.logger.info(f"Waiting {delay} seconds before next submission...")
                    await asyncio.sleep(delay)

            await browser.close()

        self.logger.info(f"\n{'='*60}")
        self.logger.info("Crawling complete!")
        self.logger.info(f"Results saved to: {output_csv}")
        self.logger.info(f"{'='*60}")

        # Print summary
        status_counts = df['status'].value_counts()
        self.logger.info("\nSummary:")
        for status, count in status_counts.items():
            self.logger.info(f"  {status}: {count}")


async def main():
    """Main entry point."""
    config = {
        'sender_name': 'Webb Hammond',
        'sender_email': 'webb@flowdrop.ai',
        'message_template': (
            "Hi [restaurant_name], I'm Webb from Flowdrop. We've built an AI agent "
            "for restaurant back office that's cheaper than MarginEdge and handles "
            "scheduling too. We're filling a small pilot group to test it. Would love "
            "to show you a quick demo: https://calendly.com/webb-flowdrop/new-meeting"
        ),
        'min_delay_seconds': 20,
        'max_delay_seconds': 40,
        'use_llm_detection': True,  # Enable LLM fallback when selectors fail (requires ANTHROPIC_API_KEY env var)
    }

    # File paths
    input_csv = 'restaurants.csv'
    output_csv = 'restaurants_results.csv'

    # Check if input file exists
    if not Path(input_csv).exists():
        print(f"Error: Input file '{input_csv}' not found!")
        print(f"Please create a CSV file with 'website_url' and 'restaurant_name' columns.")
        return

    # Create crawler and run
    crawler = ContactFormCrawler(config)

    # Start with headless=False for testing, then switch to True
    headless = True  # Set to False to see the browser in action

    await crawler.run(input_csv, output_csv, headless=headless)


if __name__ == '__main__':
    asyncio.run(main())
