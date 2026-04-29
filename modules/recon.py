import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
from colorama import Fore
from config import TIMEOUT

class ReconModule:
    def __init__(self, target):
        self.target = target
        self.visited = set()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def gather_urls(self):
        """Gather all URLs from the target"""
        urls = set()
        
        try:
            print(f"{Fore.CYAN}[*] Fetching main page: {self.target}")
            response = self.session.get(self.target, timeout=TIMEOUT, verify=False)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all links
            print(f"{Fore.CYAN}[*] Extracting links from HTML...")
            for link in soup.find_all('a', href=True):
                url = urljoin(self.target, link['href'])
                if self.is_valid_url(url):
                    urls.add(self.normalize_url(url))
            
            # Find all forms
            for form in soup.find_all('form'):
                action = form.get('action', '')
                if action:
                    url = urljoin(self.target, action)
                    if self.is_valid_url(url):
                        urls.add(self.normalize_url(url))
                
                # Also collect form inputs for parameter fuzzing
                for input_tag in form.find_all(['input', 'textarea', 'select']):
                    name = input_tag.get('name')
                    if name:
                        # Add URL with parameter template
                        param_url = f"{self.target}?{name}=FUZZ"
                        urls.add(param_url)
            
            # Try common paths
            print(f"{Fore.CYAN}[*] Checking common paths...")
            common_paths = [
                '/api', '/v1', '/admin', '/login', '/signup', '/contact',
                '/about', '/search', '/product', '/category', '/user',
                '/profile', '/settings', '/dashboard', '/panel', '/cpanel'
            ]
            
            for path in common_paths:
                test_url = urljoin(self.target, path)
                try:
                    resp = self.session.get(test_url, timeout=TIMEOUT/2, verify=False)
                    if resp.status_code == 200:
                        urls.add(test_url)
                except:
                    pass
            
            # Try to find sitemap
            sitemap_url = urljoin(self.target, 'sitemap.xml')
            try:
                sitemap_resp = self.session.get(sitemap_url, timeout=TIMEOUT/2, verify=False)
                if sitemap_resp.status_code == 200:
                    urls.update(re.findall(r'<loc>(.*?)</loc>', sitemap_resp.text))
            except:
                pass
            
            # Try robots.txt
            robots_url = urljoin(self.target, 'robots.txt')
            try:
                robots_resp = self.session.get(robots_url, timeout=TIMEOUT/2, verify=False)
                if robots_resp.status_code == 200:
                    disallowed = re.findall(r'Disallow:\s*(.*)', robots_resp.text)
                    for path in disallowed:
                        if path and path != '/':
                            urls.add(urljoin(self.target, path))
            except:
                pass
                
        except Exception as e:
            print(f"{Fore.RED}[-] Error gathering URLs: {str(e)}")
        
        # Add the target itself
        urls.add(self.target)
        
        # Also add common parameterized URLs
        common_params = ['id', 'page', 'view', 'cat', 'product', 'user', 'file', 'include']
        for param in common_params:
            urls.add(f"{self.target}?{param}=1")
        
        filtered_urls = [url for url in urls if self.is_valid_url(url)]
        
        print(f"{Fore.GREEN}[+] Discovered {len(filtered_urls)} unique URLs")
        
        return filtered_urls[:200]  # Limit to 200 URLs for performance
    
    def normalize_url(self, url):
        """Normalize URL by removing fragments"""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip('/')
    
    def is_valid_url(self, url):
        """Check if URL belongs to same domain and is valid"""
        if not url:
            return False
            
        try:
            target_domain = urlparse(self.target).netloc
            url_domain = urlparse(url).netloc
            
            # Skip external domains
            if url_domain and target_domain not in url_domain:
                return False
            
            # Skip non-http protocols
            if not url.startswith(('http://', 'https://')):
                return False
            
            # Skip common file extensions
            skip_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.css', '.js', '.ico', '.pdf', '.zip', '.tar']
            if any(url.lower().endswith(ext) for ext in skip_extensions):
                return False
            
            return True
            
        except:
            return False