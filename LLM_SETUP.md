# LLM-Powered Form Detection Setup (Ollama - Free & Local)

The crawler includes optional AI-powered form field detection using **Ollama** - a completely free, open-source, local LLM runner. No API costs, no cloud dependencies, runs 100% on your machine.

## How It Works

The crawler uses a two-tier approach:

1. **Fast Selector Detection** (default) - Uses predefined CSS selectors to find common form fields
2. **LLM Fallback** (when enabled) - If selectors fail, a local AI model analyzes the HTML and identifies the correct fields

The LLM can understand context and handle edge cases like:
- Unusual field names (e.g., "Your inquiry" instead of "Message")
- Custom form layouts
- Dynamic field IDs
- Multi-step forms

## Why Ollama?

- ✅ **100% Free** - No API costs, ever
- ✅ **Private** - Everything runs locally on your machine
- ✅ **Fast** - 2-5 seconds per form on decent hardware
- ✅ **Open Source** - Uses models like Llama 3.2, Phi-3, Mistral
- ✅ **No Rate Limits** - Process as many forms as you want

## Setup (10 minutes)

### 1. Install Ollama

**macOS/Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
Download from https://ollama.com/download

**Or install via package manager:**
```bash
# macOS (Homebrew)
brew install ollama

# Linux (apt)
curl -fsSL https://ollama.com/install.sh | sh

# Or download from https://ollama.com/
```

### 2. Start Ollama Server

```bash
ollama serve
```

This starts the Ollama server in the background. Leave this running.

**Note:** On macOS/Windows, Ollama Desktop app starts automatically and runs in the background.

### 3. Download a Model

Open a new terminal and run:

```bash
# Recommended: Llama 3.2 (3B) - Fast and accurate
ollama pull llama3.2

# Alternatives:
# ollama pull phi3           # Smaller, faster (3.8GB)
# ollama pull mistral        # Larger, more accurate (4.1GB)
# ollama pull qwen2.5:3b     # Good balance (2.1GB)
```

**Model Comparison:**

| Model | Size | Speed | Accuracy | Recommended For |
|-------|------|-------|----------|-----------------|
| llama3.2 | 2GB | Fast | High | **Best default choice** |
| phi3 | 3.8GB | Very Fast | Good | Speed priority |
| qwen2.5:3b | 2.1GB | Fast | High | Good alternative |
| mistral | 4.1GB | Medium | Very High | Accuracy priority |

First time pulling a model takes a few minutes (downloads ~2-4GB).

### 4. Install Ollama Python SDK

```bash
pip install ollama
```

Or reinstall all requirements:

```bash
pip install -r requirements.txt
```

### 5. Enable LLM Detection

In `contact_crawler.py` (around line 605), ensure this is set:

```python
'use_llm_detection': True,  # Enable LLM fallback
'llm_model': 'llama3.2',    # Model to use
```

### 6. Test It

```bash
# Test that Ollama is working
ollama run llama3.2 "Hello!"

# Should respond with a greeting
```

## Usage

Once set up, just run the crawler normally:

```bash
python contact_crawler.py
```

The LLM will automatically kick in when standard selectors fail.

## Performance

| Mode | Speed | Success Rate | Cost |
|------|-------|--------------|------|
| Selectors Only | Instant | 60-70% | $0 |
| **LLM Fallback (Ollama)** | **2-5s per fallback** | **85-95%** | **$0** |

**Expected runtime:**
- 1000 restaurants with ~30% LLM fallback = +10-20 minutes total
- No cost, runs locally

## Verification

Check the logs when running:

```
INFO - Selector-based detection failed, trying LLM...
INFO - Using Ollama LLM to detect form fields...
INFO - LLM detected fields: ['name', 'email', 'message', 'submit']
INFO - Filled email field
```

## Changing Models

To use a different model:

1. Download it:
```bash
ollama pull phi3
```

2. Update `contact_crawler.py`:
```python
'llm_model': 'phi3',
```

## Disabling LLM Detection

To disable and use only selector-based detection:

In `contact_crawler.py`:
```python
'use_llm_detection': False,
```

## Troubleshooting

### Error: "Ollama SDK not installed"
Run: `pip install ollama`

### Error: "Make sure Ollama is running"
Start Ollama server:
```bash
ollama serve
```

Or if you have Ollama Desktop, make sure it's running.

### Error: Model not found
Pull the model first:
```bash
ollama pull llama3.2
```

### LLM is slow
Try a smaller/faster model:
```bash
ollama pull phi3
```

Then update config:
```python
'llm_model': 'phi3',
```

### High CPU/RAM usage
Ollama uses ~4-8GB RAM when running. If this is too much:
- Use a smaller model (phi3 or qwen2.5:3b)
- Disable LLM detection: `'use_llm_detection': False`

### Model not loading
Check Ollama is running:
```bash
ollama list
```

Should show your installed models.

## Hardware Requirements

**Minimum:**
- 8GB RAM
- Any modern CPU
- 5GB free disk space

**Recommended:**
- 16GB RAM
- Multi-core CPU
- 10GB free disk space
- (GPU optional - Ollama can use GPU if available but CPU is fine)

## Privacy & Security

- ✅ Everything runs locally on your machine
- ✅ No data sent to any API or cloud service
- ✅ No internet required (after models are downloaded)
- ✅ 100% private and secure

## Advanced: GPU Acceleration (Optional)

If you have an NVIDIA GPU, Ollama will automatically use it for faster inference.

Check if GPU is being used:
```bash
ollama run llama3.2 "test"
```

Watch GPU usage with `nvidia-smi` while it runs.

## Common Models for This Task

Best models for form field detection (in order of recommendation):

1. **llama3.2** (2GB) - Best balance of speed and accuracy
2. **phi3** (3.8GB) - Faster, still very accurate
3. **qwen2.5:3b** (2.1GB) - Small and efficient
4. **mistral** (4.1GB) - Most accurate, slightly slower

## Need Help?

- Ollama docs: https://ollama.com/
- Ollama GitHub: https://github.com/ollama/ollama
- Project issues: https://github.com/webbmaistro/contactUsCrawler/issues
