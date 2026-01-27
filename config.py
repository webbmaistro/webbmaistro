"""
Configuration file for Contact Form Crawler
Modify these settings to customize the crawler behavior
"""

# Your information to fill in contact forms
SENDER_NAME = 'Webb Hammond'
SENDER_EMAIL = 'webb@flowdrop.ai'

# Message template - use [restaurant_name] as placeholder
MESSAGE_TEMPLATE = (
    "Hi [restaurant_name], I'm Webb from Flowdrop. We've built an AI agent "
    "for restaurant back office that's cheaper than MarginEdge and handles "
    "scheduling too. We're filling a small pilot group to test it. Would love "
    "to show you a quick demo: https://calendly.com/webb-flowdrop/new-meeting"
)

# Delay between submissions (in seconds) to avoid rate limiting
MIN_DELAY_SECONDS = 20
MAX_DELAY_SECONDS = 40

# Browser settings
HEADLESS = True  # Set to False to watch the browser in action (useful for debugging)
TIMEOUT = 15000  # Timeout for page loads in milliseconds

# LLM-Powered Form Detection (Optional - 100% Free with Ollama)
# When enabled, uses a local AI model to intelligently detect form fields if standard selectors fail
USE_LLM_DETECTION = True  # Set to False to disable LLM fallback
LLM_MODEL = 'llama3.2'  # Ollama model to use (llama3.2, phi3, mistral, qwen2.5:3b, etc.)

# To use LLM detection:
# 1. Install Ollama: curl -fsSL https://ollama.com/install.sh | sh
# 2. Pull a model: ollama pull llama3.2
# 3. Start Ollama: ollama serve (runs automatically on macOS/Windows)
# 4. Install SDK: pip install ollama
# Cost: $0 - Everything runs locally on your machine

# File paths
INPUT_CSV = 'restaurants.csv'  # Your input CSV with website_url and restaurant_name columns
OUTPUT_CSV = 'restaurants_results.csv'  # Output file with results

# Additional contact page URL patterns to try (in addition to defaults)
CUSTOM_CONTACT_PATTERNS = [
    # Add any custom patterns specific to your target websites
    # '/reservations',
    # '/inquiries',
]

# Additional link text patterns to search for (in addition to defaults)
CUSTOM_LINK_TEXT_PATTERNS = [
    # Add any custom link text patterns
    # 'book now',
    # 'inquire',
]
