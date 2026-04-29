import requests
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from colorama import Fore
from config import TIMEOUT

class XSSScanner:
    def __init__(self, target, ai_detector=None):
        self.target = target
        self.ai_detector = ai_detector
        self.payloads = self.load_payloads()
        self.session = requests.Session()
    
    def load_payloads(self):
        """Load XSS payloads"""
        return [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert(1)>",
            "javascript:alert('XSS')",
            "<svg/onload=alert(1)>",
            "'><script>alert(1)</script>",
            "\"><script>alert(1)</script>",
            "><script>alert(1)</script>",
            "<body onload=alert(1)>",
            "<input onfocus=alert(1) autofocus>",
            "<iframe src=javascript:alert(1)>",
            "javascript:alert(document.cookie)",
            "<script>confirm(1)</script>",
            "«script»alert(1)«/script»",
            "<img src=\"x\" onerror=\"alert(1)\">",
        ]
    
    def scan(self, url):
        """Scan URL for XSS vulnerabilities"""
        vulnerabilities = []
        
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        if not params:
            return vulnerabilities
        
        for param in params.keys():
            for payload in self.payloads:
                test_params = params.copy()
                test_params[param] = [payload]
                new_query = urlencode(test_params, doseq=True)
                test_url = urlunparse((
                    parsed.scheme, parsed.netloc, parsed.path,
                    parsed.params, new_query, parsed.fragment
                ))
                
                try:
                    response = self.session.get(test_url, timeout=TIMEOUT, verify=False)
                    
                    # Check if payload is reflected without encoding
                    is_vulnerable = payload in response.text
                    
                    # Also check for encoded versions
                    if not is_vulnerable:
                        import html
                        if html.escape(payload) in response.text:
                            is_vulnerable = True
                    
                    # AI verification
                    if self.ai_detector and not is_vulnerable:
                        is_vulnerable, confidence = self.ai_detector.predict(response.text)
                        if confidence < 0.70:
                            is_vulnerable = False
                    
                    if is_vulnerable:
                        vuln = {
                            'type': 'Cross-Site Scripting (XSS)',
                            'url': test_url[:200],
                            'parameter': param,
                            'payload': payload[:50],
                            'severity': 'Medium',
                            'evidence': f'Payload reflected in response: {payload[:50]}'
                        }
                        vulnerabilities.append(vuln)
                        print(f"{Fore.RED}[!] XSS Found: {test_url[:100]}")
                        
                except:
                    pass
        
        return vulnerabilities