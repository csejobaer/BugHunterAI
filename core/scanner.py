import concurrent.futures
import threading
from urllib.parse import urlparse
from colorama import Fore

from modules.sqli_scanner import SQLIScanner
from modules.xss_scanner import XSSScanner
from modules.lfi_scanner import LFIScanner
from modules.idor_scanner import IDORScanner
from core.reporter import Reporter
from core.ai_detector import AIDetector
from config import ENABLED_MODULES, TIMEOUT

class Scanner:
    def __init__(self, target, threads, ai_enabled):
        self.target = target
        self.threads = threads
        self.ai_enabled = ai_enabled
        self.reporter = Reporter()
        self.ai_detector = AIDetector() if ai_enabled else None
        self.scanned_urls = set()
        self.lock = threading.Lock()
        
        # Initialize scanners
        self.scanners = []
        if 'sqli' in ENABLED_MODULES:
            self.scanners.append(SQLIScanner(target, ai_detector=self.ai_detector))
        if 'xss' in ENABLED_MODULES:
            self.scanners.append(XSSScanner(target, ai_detector=self.ai_detector))
        if 'lfi' in ENABLED_MODULES:
            self.scanners.append(LFIScanner(target, ai_detector=self.ai_detector))
        if 'idor' in ENABLED_MODULES:
            self.scanners.append(IDORScanner(target, ai_detector=self.ai_detector))
        
        print(f"{Fore.GREEN}[+] Initialized {len(self.scanners)} scanner modules")
    
    def scan_all(self, urls):
        """Scan all URLs for vulnerabilities"""
        vulnerabilities = []
        
        # Filter unique URLs
        unique_urls = list(set(urls))
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.threads) as executor:
            future_to_url = {executor.submit(self.scan_single, url): url for url in unique_urls}
            
            for i, future in enumerate(concurrent.futures.as_completed(future_to_url), 1):
                url = future_to_url[future]
                try:
                    results = future.result(timeout=TIMEOUT * 2)
                    if results:
                        vulnerabilities.extend(results)
                    
                    # Progress indicator
                    if i % 10 == 0:
                        print(f"{Fore.CYAN}[*] Progress: {i}/{len(unique_urls)} URLs scanned")
                        
                except concurrent.futures.TimeoutError:
                    print(f"{Fore.YELLOW}[!] Timeout scanning {url[:80]}")
                except Exception as e:
                    print(f"{Fore.RED}[-] Error scanning {url[:80]}: {str(e)[:50]}")
        
        return vulnerabilities
    
    def scan_single(self, url):
        """Scan a single URL with all modules"""
        # Skip if already scanned
        with self.lock:
            if url in self.scanned_urls:
                return []
            self.scanned_urls.add(url)
        
        results = []
        
        # Skip non-http URLs
        if not url.startswith(('http://', 'https://')):
            return []
        
        # Scan with each module
        for scanner in self.scanners:
            try:
                vulns = scanner.scan(url)
                if vulns:
                    results.extend(vulns)
            except Exception as e:
                # Silent fail for individual modules
                pass
        
        return results