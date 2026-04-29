# Bug Hunter AI 🔍

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=venom&height=250&text=BugHunter%20AI&fontSize=50&color=0:000000,100:00ff9c&stroke=00ff9c&animation=fadeIn&fontColor=00ff9c" width="100%"/>
</p>

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Orbitron&size=28&duration=2200&pause=800&color=00FF9C&center=true&vCenter=true&width=900&lines=AI+Powered+Bug+Hunting;Advanced+Security+Scanner;Exploit+Detection+Engine;Cyber+Intelligence+System;Built+for+Ethical+Hackers" />
</p>


<p align="center">
  <img src="https://img.shields.io/badge/AI-Powered-00ff9c?style=for-the-badge&logo=openai&logoColor=black">
  <img src="https://img.shields.io/badge/Security-Scanner-red?style=for-the-badge">
  <img src="https://img.shields.io/badge/Bug%20Hunter-Elite-black?style=for-the-badge">
</p>



## 📋 Features

- ✅ **SQL Injection Detection** (Error, Union, Time-based)
- ✅ **XSS Detection** (Reflected & DOM-based)
- ✅ **LFI/RFI Detection**
- ✅ **IDOR Detection**
- ✅ **AI-Powered Detection** (Reduces false positives)
- ✅ **Multi-threaded Scanning** (Up to 20 threads)
- ✅ **Beautiful HTML/JSON/Text Reports**
- ✅ **Reconnaissance Module**

---

## 🚀 Quick Installation

```bash
# Clone repository
git clone https://github.com/csejobaer/BugHunterAI.git
cd bug-hunter-ai

#Use a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run scan
python main.py -u http://testphp.vulnweb.com
```

---

## 📁 Project Structure

```
bug-hunter-ai/
│
├── main.py                 # Main entry point
├── config.py               # Configuration settings
├── requirements.txt        # Dependencies
│
├── core/                   # Core modules
│   ├── scanner.py         # Scanner engine
│   ├── ai_detector.py     # AI detection model
│   └── reporter.py        # Report generator
│
├── modules/                # Scanner modules
│   ├── sqli_scanner.py    # SQL injection
│   ├── xss_scanner.py     # XSS detection
│   ├── lfi_scanner.py     # LFI detection
│   ├── idor_scanner.py    # IDOR detection
│   └── recon.py           # Reconnaissance
│
├── reports/                # Generated reports
├── models/                 # Trained AI models
└── payloads/              # Payload files
```

---

## 🔧 Usage Examples

### Basic Scan
```bash
python main.py -u https://example.com
```

### Advanced Scan with Custom Threads
```bash
python main.py -u https://example.com -t 20
```

### Disable AI Detection
```bash
python main.py -u https://example.com --no-ai
```

### Custom Timeout
```bash
python main.py -u https://example.com --timeout 15
```

### Command Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `-u, --url` | Target URL (required) | - |
| `-t, --threads` | Number of threads | 10 |
| `--no-ai` | Disable AI detection | False |
| `--timeout` | Request timeout (seconds) | 10 |

---

## 📊 Sample Output

```
╔════════════════════════════════════════════════════════════════╗
║         Bug Hunter AI - Professional Tool                      ║
╚════════════════════════════════════════════════════════════════╝

[+] Target: http://testphp.vulnweb.com
[+] AI Detection: Enabled
[+] Threads: 10

[*] Phase 1: Reconnaissance...
[+] Found 45 unique URLs

[*] Phase 2: Vulnerability Scanning...
[!] SQLi Found: http://testphp.vulnweb.com/artists.php?artist=1'
[!] XSS Found: http://testphp.vulnweb.com/search.php?search=<script>

[+] Scan Completed!
[+] Total Vulnerabilities Found: 3

[+] Reports saved to:
    📄 JSON: reports/report_20240101_120000.json
    🌐 HTML: reports/report_20240101_120000.html
```

---

## 📄 Reports

The tool generates three report formats:

1. **HTML Report** - Beautiful interactive web report
2. **JSON Report** - Machine-readable format
3. **Text Report** - Simple plain text output

Reports include:
- Vulnerability type & severity
- Affected URL & parameter
- Payload used
- Evidence/Screenshots
- CVSS scoring

---

## ⚙️ Configuration

Edit `config.py` to customize:

```python
# Scanner settings
MAX_THREADS = 10
TIMEOUT = 10
DELAY = 0.5

# AI Settings
AI_CONFIDENCE_THRESHOLD = 0.75

# Enabled modules
ENABLED_MODULES = ['sqli', 'xss', 'lfi', 'idor']
```

---

## 🛠️ Requirements

- Python 3.8+
- requests
- beautifulsoup4
- scikit-learn
- colorama
- jinja2

Full list in `requirements.txt`

---

## 📝 Legal Disclaimer

> **IMPORTANT:** This tool is for **educational and authorized testing purposes only**.
>
> - Only scan websites you own or have written permission to test
 - Unauthorized scanning is illegal in most jurisdictions
 - The author assumes no liability for misuse
- Always follow responsible disclosure practices

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📧 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/csejobaer/BugHunterAI/issues)
- **Security**: Private disclosure only

---

## ⭐ Show Your Support

If this tool helped you, please give it a star ⭐ on GitHub!

---

<div align="center">

**Made with ❤️ for the security community**

**[⬆ Back to Top](#bug-hunter-ai-)**

</div>
