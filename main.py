#!/usr/bin/env python3
import sys
import argparse
import time
import threading
from colorama import init, Fore, Style
from datetime import datetime
from urllib.parse import urlparse

from config import MAX_THREADS, TIMEOUT
from core.scanner import Scanner
from modules.recon import ReconModule

init(autoreset=True)

class BugHunterAI:
    def __init__(self, target, threads=10, ai_enabled=True):
        self.target = target.rstrip('/')
        self.threads = min(threads, MAX_THREADS)
        self.ai_enabled = ai_enabled
        self.scanner = None
        self.recon = ReconModule(target)
        self.start_time = None
        self.end_time = None
        self.vulnerabilities = []
        self.lock = threading.Lock()
        
    def banner(self):
        banner_text = f"""
{Fore.CYAN}╔════════════════════════════════════════════════════════════════╗
║                                                                    ║
║  {Fore.RED}██████╗ ██╗   ██╗ ██████╗     ██╗  ██╗██╗   ██╗███╗   ██╗████████╗{Fore.CYAN}║
║  {Fore.RED}██╔══██╗██║   ██║██╔════╝     ██║  ██║██║   ██║████╗  ██║╚══██╔══╝{Fore.CYAN}║
║  {Fore.RED}██████╔╝██║   ██║██║  ███╗    ███████║██║   ██║██╔██╗ ██║   ██║   {Fore.CYAN}║
║  {Fore.RED}██╔══██╗██║   ██║██║   ██║    ██╔══██║██║   ██║██║╚██╗██║   ██║   {Fore.CYAN}║
║  {Fore.RED}██████╔╝╚██████╔╝╚██████╔╝    ██║  ██║╚██████╔╝██║ ╚████║   ██║   {Fore.CYAN}║
║  {Fore.RED}╚═════╝  ╚═════╝  ╚═════╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   {Fore.CYAN}║
║                                                                    ║
║         {Fore.YELLOW}Professional Bug Hunting Tool with AI{Fore.CYAN}                     ║
║                      Version 1.0.0                               ║
╚════════════════════════════════════════════════════════════════╝
        """
        print(banner_text)
        print(f"{Fore.GREEN}[+] Target: {self.target}")
        print(f"{Fore.GREEN}[+] AI Detection: {'Enabled' if self.ai_enabled else 'Disabled'}")
        print(f"{Fore.GREEN}[+] Threads: {self.threads}")
        print(f"{Fore.GREEN}[+] Timeout: {TIMEOUT}s")
        print("-" * 68)
        
    def run(self):
        self.banner()
        self.start_time = time.time()
        
        # Phase 1: Reconnaissance
        print(f"{Fore.YELLOW}[*] Phase 1: Starting Reconnaissance...")
        urls = self.recon.gather_urls()
        print(f"{Fore.GREEN}[+] Found {len(urls)} unique URLs")
        
        if not urls:
            print(f"{Fore.RED}[-] No URLs found. Exiting...")
            return []
        
        # Show some URLs
        print(f"{Fore.CYAN}[*] Sample URLs:")
        for url in urls[:5]:
            print(f"    - {url}")
        
        # Phase 2: Initialize scanner
        print(f"\n{Fore.YELLOW}[*] Phase 2: Initializing Scanner Modules...")
        self.scanner = Scanner(self.target, self.threads, self.ai_enabled)
        
        # Phase 3: Vulnerability Scanning
        print(f"{Fore.YELLOW}[*] Phase 3: Starting Vulnerability Scanning...")
        print(f"{Fore.CYAN}[*] This may take some time depending on the number of URLs...\n")
        
        self.vulnerabilities = self.scanner.scan_all(urls)
        
        # Phase 4: Reporting
        print(f"\n{Fore.YELLOW}[*] Phase 4: Generating Report...")
        self.end_time = time.time()
        total_time = self.end_time - self.start_time
        
        # Print summary
        self.print_summary(total_time)
        
        # Save report
        if self.scanner.reporter:
            self.scanner.reporter.save_report(self.vulnerabilities, total_time)
        
        return self.vulnerabilities
    
    def print_summary(self, total_time):
        print("\n" + "=" * 68)
        print(f"{Fore.CYAN}[+] SCAN COMPLETED!")
        print(f"{Fore.CYAN}[+] Total Time: {total_time:.2f} seconds")
        print(f"{Fore.CYAN}[+] Total URLs Scanned: {len(self.scanner.scanned_urls) if self.scanner else 0}")
        print(f"{Fore.CYAN}[+] Total Vulnerabilities Found: {len(self.vulnerabilities)}")
        
        if self.vulnerabilities:
            print(f"\n{Fore.RED}[!] VULNERABILITIES SUMMARY:")
            print(f"{Fore.RED}    {'=' * 50}")
            
            vuln_types = {}
            for vuln in self.vulnerabilities:
                vuln_type = vuln.get('type', 'Unknown')
                vuln_types[vuln_type] = vuln_types.get(vuln_type, 0) + 1
            
            for vuln_type, count in vuln_types.items():
                severity = self.get_severity_color(vuln_type)
                print(f"    {severity}[{count}] {vuln_type}")
            
            print(f"\n{Fore.YELLOW}[*] Detailed findings:")
            for i, vuln in enumerate(self.vulnerabilities[:10], 1):
                print(f"    {i}. [{vuln.get('severity', 'Info')}] {vuln.get('type')}")
                print(f"       URL: {vuln.get('url', 'N/A')[:80]}")
                if vuln.get('parameter'):
                    print(f"       Parameter: {vuln.get('parameter')}")
        else:
            print(f"\n{Fore.GREEN}[✓] No vulnerabilities found! Your application appears secure.")
        
        print("=" * 68)
    
    def get_severity_color(self, vuln_type):
        if 'SQL' in vuln_type or 'LFI' in vuln_type:
            return f"{Fore.RED}"
        elif 'XSS' in vuln_type:
            return f"{Fore.YELLOW}"
        else:
            return f"{Fore.CYAN}"

def validate_url(url):
    if not url.startswith(('http://', 'https://')):
        return f"http://{url}"
    return url

def main():
    parser = argparse.ArgumentParser(
        description='Bug Hunter AI - Professional Web Vulnerability Scanner',
        epilog='Example: python main.py -u http://testphp.vulnweb.com -t 20'
    )
    parser.add_argument('-u', '--url', required=True, help='Target URL (e.g., http://example.com)')
    parser.add_argument('-t', '--threads', type=int, default=10, help='Number of threads (default: 10, max: 20)')
    parser.add_argument('--no-ai', action='store_true', help='Disable AI detection')
    parser.add_argument('--timeout', type=int, default=10, help='Request timeout in seconds (default: 10)')
    
    args = parser.parse_args()
    
    # Update global timeout
    global TIMEOUT
    TIMEOUT = args.timeout
    
    # Validate and fix URL
    target_url = validate_url(args.url)
    
    # Create and run scanner
    hunter = BugHunterAI(
        target=target_url,
        threads=min(args.threads, 20),
        ai_enabled=not args.no_ai
    )
    
    try:
        vulnerabilities = hunter.run()
        
        # Exit with appropriate code
        if vulnerabilities:
            sys.exit(1)  # Vulnerabilities found
        else:
            sys.exit(0)  # No vulnerabilities
            
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] Scan interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"{Fore.RED}[-] Fatal Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()