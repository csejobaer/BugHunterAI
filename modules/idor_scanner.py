import requests
from urllib.parse import urlparse
import re
from colorama import Fore
from config import TIMEOUT

class IDORScanner:
    def __init__(self, target, ai_detector=None):
        self.target = target
        self.ai_detector = ai_detector
        self.session = requests.Session()
    
    def find_ids_in_url(self, url):
        """Find numeric IDs in URL"""
        patterns = [
            r'[?&;]id[=:](\d+)',
            r'[?&;]user[=:](\d+)',
            r'[?&;]uid[=:](\d+)',
            r'[?&;]pid[=:](\d+)',
            r'[?&;]prod[=:](\d+)',
            r'[?&;]product[=:](\d+)',
            r'[?&;]page[=:](\d+)',
            r'[?&;]view[=:](\d+)',
            r'/(\d+)(?:/|$|\?)',
        ]
        
        ids = []
        for pattern in patterns:
            matches = re.findall(pattern, url)
            ids.extend(matches)
        
        # Filter unique IDs
        return list(set(ids))
    
    def scan(self, url):
        """Scan for IDOR vulnerabilities"""
        vulnerabilities = []
        ids = self.find_ids_in_url(url)
        
        if not ids:
            return vulnerabilities
        
        # Get original response for comparison
        try:
            original_response = self.session.get(url, timeout=TIMEOUT, verify=False)
            original_content = original_response.text[:500]  # Compare first 500 chars
        except:
            return vulnerabilities
        
        for id_value in ids[:3]:  # Test first 3 IDs only to avoid too many requests
            try:
                # Try to increment ID
                incremented = str(int(id_value) + 1)
                test_url = url.replace(id_value, incremented)
                
                response = self.session.get(test_url, timeout=TIMEOUT, verify=False)
                
                # Check if we got different content (potential IDOR)
                if response.status_code == 200 and original_response.status_code == 200:
                    # If content is significantly different
                    if len(response.text) > 100 and len(original_content) > 100:
                        if response.text[:500] != original_content:
                            vuln = {
                                'type': 'Insecure Direct Object Reference (IDOR)',
                                'url': test_url[:200],
                                'parameter': 'ID parameter',
                                'payload': f'Changed ID from {id_value} to {incremented}',
                                'severity': 'Medium',
                                'evidence': f'Different content returned with modified ID (status: {response.status_code})'
                            }
                            vulnerabilities.append(vuln)
                            print(f"{Fore.RED}[!] Possible IDOR Found: {test_url[:100]}")
                            
            except (ValueError, requests.exceptions.RequestException):
                pass
        
        return vulnerabilities