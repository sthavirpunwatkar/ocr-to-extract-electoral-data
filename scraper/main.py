import requests
from bs4 import BeautifulSoup
import os
import urllib3
import time
import json

# Suppress insecure request warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class VoterScraper:
    def __init__(self, config_path="config.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.base_url = self.config["base_url"]
        self.output_dir = self.config.get("output_dir", "downloads")
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def get_initial_token(self):
        print(f"Initializing session at {self.base_url}...")
        res = self.session.get(self.base_url, verify=False)
        soup = BeautifulSoup(res.text, 'html.parser')
        token = soup.find('input', {'name': '__RequestVerificationToken'})['value']
        return token

    def download_pdf(self, url, referer, filename):
        print(f"  Downloading PDF: {filename}...")
        headers = {"Referer": referer}
        try:
            res = self.session.get(url, verify=False, headers=headers, timeout=60)
            if res.status_code == 200 and res.headers.get('Content-Type') == 'application/pdf':
                filepath = os.path.join(self.output_dir, filename)
                with open(filepath, 'wb') as f:
                    f.write(res.content)
                print(f"  Saved {filename}")
                return True
        except Exception as e:
            print(f"  Error: {e}")
        return False

    def run(self):
        token = self.get_initial_token()
        
        for district_id, local_bodies in self.config["districts"].items():
            for lb_id in local_bodies:
                print(f"Processing District {district_id}, LB {lb_id}...")
                
                # Search POST
                data = {
                    "__RequestVerificationToken": token,
                    "ListType": "Final",
                    "District": district_id,
                    "LocalBody": "9",
                    "LocalBodyName": lb_id,
                    "ServerOne": "Search on Server one"
                }
                
                resp = self.session.post(self.base_url, data=data, verify=False)
                soup = BeautifulSoup(resp.text, 'html.parser')
                
                # Authorization Step
                inner_form = soup.find('form', action=lambda x: x and '/pdf/CitizenSearchPdf' in x)
                if inner_form:
                    inner_action = inner_form['action']
                    inner_token = inner_form.find('input', {'name': '__RequestVerificationToken'})['value']
                    
                    if not inner_action.startswith('http'):
                        host = "https://115.124.105.88" if "115.124.105.88" in resp.url else "https://mahasecvoterlist.in"
                        inner_action = host + inner_action
                    
                    auth_res = self.session.post(inner_action, data={"__RequestVerificationToken": inner_token}, verify=False)
                    
                    # Download Step
                    auth_soup = BeautifulSoup(auth_res.text, 'html.parser')
                    links = auth_soup.find_all('a', href=True)
                    for i, link in enumerate([l['href'] for l in links if 'Download' in l['href'] or '.pdf' in l['href'].lower()]):
                        url = link if link.startswith('http') else ("https://115.124.105.88" + link if "115.124.105.88" in auth_res.url else "https://mahasecvoterlist.in" + link)
                        fname = f"dist_{district_id}_lb_{lb_id}_{i+1}.pdf"
                        self.download_pdf(url, auth_res.url, fname)
                
                time.sleep(self.config.get("delay", 1))

if __name__ == "__main__":
    scraper = VoterScraper()
    scraper.run()
