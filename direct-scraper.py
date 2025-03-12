import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
from urllib.parse import urljoin

class DirectUSCClassScraper:
    def __init__(self, term="20253"):
        """
        Initialize the USC Class Scraper
        
        Parameters:
        term (str): The term code to scrape (default: "20253" for Spring 2025)
        """
        self.term = term
        self.base_url = f"https://classes.usc.edu/term-{term}/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Create directory for downloaded files
        self.download_dir = "usc_class_data"
        os.makedirs(self.download_dir, exist_ok=True)
        
        # Known departments to try directly
        self.known_departments = [
            'csci', 'math', 'buad', 'econ', 'engr', 'psyc', 'comm', 'bisc',
            'acct', 'ahis', 'amst', 'anth', 'astr', 'bioc', 'chem', 'clas',
            'engl', 'fren', 'geog', 'germ', 'hist', 'ital', 'ling', 'phil',
            'phys', 'poir', 'soci', 'span', 'art', 'arth', 'asc', 'baep', 
            'biol', 'bme', 'ce', 'chem', 'cmgt', 'ctin', 'dsci', 'ealc',
            'ee', 'fbe', 'fren', 'geol', 'gero', 'hbio', 'iml', 'ir',
            'itp', 'jour', 'law', 'lim', 'masc', 'mda', 'mech', 'mpw',
            'mptx', 'ms', 'musc', 'naut', 'neur', 'nsci', 'ppe', 'phed',
            'ppa', 'ppd', 'pte', 'ptx', 'rel', 'rus', 'swms', 'thtr', 
            'visi', 'writ'
        ]
    
    def download_department_csv(self, dept_code):
        """
        Download the CSV file for a specific department
        
        Parameters:
        dept_code (str): The department code (e.g., 'csci')
        
        Returns:
        str: Path to the downloaded file, or None if download failed
        """
        dept_url = f"{self.base_url}classes/{dept_code}"
        print(f"Processing department: {dept_code} ({dept_url})")
        
        try:
            # Get the department page
            response = self.session.get(dept_url)
            if response.status_code != 200:
                print(f"  Failed to access {dept_url}, status code: {response.status_code}")
                return None
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for CSV download link
            csv_link = None
            download_links = soup.select('a[href$=".csv"]')
            
            if download_links:
                for link in download_links:
                    link_text = link.get_text(strip=True).lower()
                    href = link.get('href')
                    print(f"  Found potential CSV link: {href}")
                    if "download" in link_text.lower() or "csv" in link_text.lower():
                        csv_link = href
                        break
            
            if not csv_link and download_links:
                # Just use the first CSV link we found
                csv_link = download_links[0].get('href')
            
            if csv_link:
                # Make sure we have the full URL
                if not csv_link.startswith('http'):
                    csv_link = urljoin(dept_url, csv_link)
                
                print(f"  Downloading from {csv_link}")
                
                # Download the CSV file
                csv_response = self.session.get(csv_link)
                if csv_response.status_code == 200:
                    file_path = os.path.join(self.download_dir, f"{dept_code}_classes.csv")
                    with open(file_path, 'wb') as f:
                        f.write(csv_response.content)
                    print(f"  Downloaded CSV to {file_path}")
                    return file_path
                else:
                    print(f"  Failed to download CSV, status code: {csv_response.status_code}")
            else:
                print(f"  No CSV link found for {dept_code}")
            
            return None
        
        except Exception as e:
            print(f"  Error processing {dept_code}: {str(e)}")
            return None
    
    def process_csv_file(self, file_path):
        """
        Process a downloaded CSV file and extract class data
        
        Parameters:
        file_path (str): Path to the CSV file
        
        Returns:
        pandas.DataFrame: DataFrame with the CSV data
        """
        try:
            df = pd.read_csv(file_path)
            print(f"  Processed {len(df)} classes from {file_path}")
            
            # Add department column if not present
            if 'Department' not in df.columns:
                dept_code = os.path.basename(file_path).split('_')[0].upper()
                df['Department'] = dept_code
                
            return df
        except Exception as e:
            print(f"  Error processing CSV {file_path}: {str(e)}")
            return None
    
    def scrape_departments(self):
        """
        Scrape class data for all known departments
        
        Returns:
        pandas.DataFrame: DataFrame containing all classes
        """
        all_dfs = []
        
        for dept in self.known_departments:
            # Add a short delay to avoid overloading the server
            time.sleep(1)
            
            # Download the department CSV
            file_path = self.download_department_csv(dept)
            if file_path:
                df = self.process_csv_file(file_path)
                if df is not None and not df.empty:
                    all_dfs.append(df)
        
        if not all_dfs:
            print("No data was collected!")
            return None
            
        # Combine all dataframes
        all_classes_df = pd.concat(all_dfs, ignore_index=True)
        
        # Save the combined data
        output_path = "usc_all_classes.csv"
        all_classes_df.to_csv(output_path, index=False)
        
        print(f"\nScraping complete!")
        print(f"Total classes scraped: {len(all_classes_df)}")
        print(f"Data saved to {output_path}")
        
        # Try to save as Excel too if openpyxl is installed
        try:
            import openpyxl
            excel_path = "usc_all_classes.xlsx"
            all_classes_df.to_excel(excel_path, index=False)
            print(f"Data also saved to {excel_path}")
        except ImportError:
            print("Note: openpyxl not installed, Excel file not created")
            print("To save as Excel, install openpyxl: pip install openpyxl")
        
        return all_classes_df

# Save memory for large datasets
def optimize_memory(df):
    """Optimize DataFrame memory usage"""
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].astype('category')
    return df

# Entry point
if __name__ == "__main__":
    scraper = DirectUSCClassScraper()
    df = scraper.scrape_departments()
    
    if df is not None:
        # Print summary info
        print("\nSummary of collected data:")
        print(f"Total rows: {len(df)}")
        print(f"Columns: {', '.join(df.columns)}")
        print("\nSample of data (first 5 rows):")
        print(df.head(5))
