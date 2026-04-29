import json
import os
from datetime import datetime
from jinja2 import Template
import pdfkit

class Reporter:
    def __init__(self):
        self.report_dir = "reports"
        os.makedirs(self.report_dir, exist_ok=True)
    
    def save_report(self, vulnerabilities, scan_time):
        """Save report in HTML/JSON format"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # JSON report
        json_report = {
            'scan_time': timestamp,
            'duration': scan_time,
            'total_vulnerabilities': len(vulnerabilities),
            'vulnerabilities': vulnerabilities
        }
        
        json_path = os.path.join(self.report_dir, f"report_{timestamp}.json")
        with open(json_path, 'w') as f:
            json.dump(json_report, f, indent=2)
        
        # HTML report
        html_path = os.path.join(self.report_dir, f"report_{timestamp}.html")
        self.generate_html_report(vulnerabilities, scan_time, html_path)
        
        print(f"\n[+] Report saved to:")
        print(f"    - {json_path}")
        print(f"    - {html_path}")
        
        return json_path
    
    def generate_html_report(self, vulnerabilities, scan_time, output_path):
        """Generate beautiful HTML report"""
        template_str = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Bug Hunter AI - Scan Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; background: #f0f0f0; }
                .container { max-width: 1200px; margin: auto; background: white; padding: 20px; border-radius: 10px; }
                h1 { color: #333; border-bottom: 3px solid #4CAF50; }
                .summary { background: #e8f5e9; padding: 15px; border-radius: 5px; margin: 20px 0; }
                .vuln { background: #ffebee; padding: 15px; margin: 10px 0; border-left: 5px solid #f44336; border-radius: 3px; }
                .vuln h3 { margin: 0 0 10px 0; color: #d32f2f; }
                .severity-high { color: #f44336; font-weight: bold; }
                .severity-medium { color: #ff9800; font-weight: bold; }
                .details { font-family: monospace; font-size: 12px; margin-top: 10px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔍 Bug Hunter AI - Vulnerability Scan Report</h1>
                
                <div class="summary">
                    <h2>Scan Summary</h2>
                    <p><strong>Scan Time:</strong> {{ timestamp }}</p>
                    <p><strong>Duration:</strong> {{ "%.2f"|format(scan_time) }} seconds</p>
                    <p><strong>Total Vulnerabilities Found:</strong> {{ vulnerabilities|length }}</p>
                </div>
                
                <h2>Vulnerabilities Details</h2>
                {% if vulnerabilities %}
                    {% for vuln in vulnerabilities %}
                    <div class="vuln">
                        <h3>{{ vuln.type }}</h3>
                        <p><strong>URL:</strong> {{ vuln.url }}</p>
                        <p><strong>Parameter:</strong> {{ vuln.parameter }}</p>
                        <p><strong>Severity:</strong> <span class="severity-{{ vuln.severity.lower() }}">{{ vuln.severity }}</span></p>
                        <p><strong>Payload:</strong> <code>{{ vuln.payload }}</code></p>
                        <p><strong>Evidence:</strong> {{ vuln.evidence }}</p>
                    </div>
                    {% endfor %}
                {% else %}
                    <p style="color: green;">✅ No vulnerabilities found! Your application is secure.</p>
                {% endif %}
            </div>
        </body>
        </html>
        """
        
        template = Template(template_str)
        html_content = template.render(
            vulnerabilities=vulnerabilities,
            scan_time=scan_time,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)