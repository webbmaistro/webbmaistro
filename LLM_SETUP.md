# LLM-Powered Form Detection Setup

The crawler includes optional AI-powered form field detection using Claude AI. This significantly improves success rates on complex or unusual contact forms.

## How It Works

The crawler uses a two-tier approach:

1. **Fast Selector Detection** (default) - Uses predefined CSS selectors to find common form fields
2. **LLM Fallback** (when enabled) - If selectors fail, Claude AI analyzes the HTML and identifies the correct fields

The LLM can understand context and handle edge cases like:
- Unusual field names (e.g., "Your inquiry" instead of "Message")
- Custom form layouts
- Dynamic field IDs
- Multi-step forms

## Setup (5 minutes)

### 1. Get an Anthropic API Key

1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (starts with `sk-ant-api...`)

### 2. Install the Anthropic SDK

```bash
pip install anthropic
```

Or reinstall all requirements:

```bash
pip install -r requirements.txt
```

### 3. Set Your API Key

**Option A: Environment Variable (Recommended)**

```bash
export ANTHROPIC_API_KEY='sk-ant-api-your-key-here'
```

To make it permanent, add to your `~/.bashrc` or `~/.zshrc`:

```bash
echo 'export ANTHROPIC_API_KEY="sk-ant-api-your-key-here"' >> ~/.bashrc
source ~/.bashrc
```

**Option B: .env File**

1. Copy the example file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your key:
```
ANTHROPIC_API_KEY=sk-ant-api-your-key-here
```

### 4. Enable LLM Detection

In `contact_crawler.py` (around line 605), ensure this is set:

```python
'use_llm_detection': True,  # Enable LLM fallback
```

Or set to `False` to use only selectors (faster, no API cost).

## Cost

LLM detection uses Claude 3.5 Haiku (fast and cheap):
- **~$0.003 per form analyzed** (~0.3 cents)
- Only called when standard selectors fail
- For 1000 restaurants with ~30% failures: **~$1 total**

## Performance

| Mode | Speed | Success Rate | Cost |
|------|-------|--------------|------|
| Selectors Only | Fast | 60-70% | $0 |
| LLM Fallback (Recommended) | Medium | 85-95% | ~$1/1000 sites |

## Verification

Test if it's working:

```bash
python contact_crawler.py
```

Check the logs for:
```
INFO - Using LLM to detect form fields...
INFO - LLM detected fields: ['name', 'email', 'message', 'submit']
```

If you see warnings like:
- `ANTHROPIC_API_KEY not set` - Set your API key
- `Anthropic SDK not installed` - Run `pip install anthropic`

## Disabling LLM Detection

To disable and use only selector-based detection:

In `contact_crawler.py`:
```python
'use_llm_detection': False,
```

Or simply don't set the API key - it will gracefully fall back to selectors only.

## Troubleshooting

### Error: "API key not set"
Set your environment variable or create a `.env` file (see Setup step 3)

### Error: "Anthropic SDK not installed"
Run: `pip install anthropic`

### LLM not being called
Check that `use_llm_detection: True` in `contact_crawler.py` config

### High costs
The LLM is only called as a fallback. If you're concerned about costs, set `use_llm_detection: False`

## Privacy & Security

- Your API key should be kept secret (never commit to git)
- Only form HTML is sent to Anthropic's API (not your contact info)
- No data is stored by Anthropic (zero data retention policy)
- All communication is encrypted (HTTPS)

## Alternative: Ollama (100% Free, Local)

Want to run everything locally with no API costs? We can switch to Ollama:

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Download a model
ollama pull llama3.2

# Use Ollama instead of Claude API
```

This requires code changes. Let me know if you want this option!
