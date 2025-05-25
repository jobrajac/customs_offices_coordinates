import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import zipfile
import os
from pathlib import Path
import time

def create_session():
    """Create a requests session with retry logic and proper headers."""
    session = requests.Session()
    
    # Configure retry strategy
    retry_strategy = Retry(
        total=5,  # number of retries
        backoff_factor=1,  # wait 1, 2, 4, 8, 16 seconds between retries
        status_forcelist=[500, 502, 503, 504]  # retry on these status codes
    )
    
    # Apply retry strategy to both http and https
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    # Add headers to mimic a browser request
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    })
    
    return session

def download_customs_data():
    """Download and extract customs offices data from the EU website."""
    
    url = "https://ec.europa.eu/taxation_customs/dds2/rd/compressed_file/data_download/RD_ICS2_CustomsOffices.zip"
    zip_filename = "RD_ICS2_CustomsOffices.zip"
    xml_filename = "RD_ICS2_CustomsOffices.xml"
    
    print(f"Downloading customs offices data from {url}...")
    print("This may take a few minutes due to retry logic if the server is busy...")
    
    try:
        # Create session with retry logic
        session = create_session()
        
        # Download the zip file with timeout
        response = session.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        # Save the zip file
        with open(zip_filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # filter out keep-alive chunks
                    f.write(chunk)
        
        print(f"Successfully downloaded {zip_filename}")
        
        # Extract the XML file
        print(f"Extracting {xml_filename}...")
        with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
            zip_ref.extractall('.')
        
        print(f"Successfully extracted {xml_filename}")
        
        # Verify the files exist
        zip_path = Path(zip_filename)
        xml_path = Path(xml_filename)
        
        if zip_path.exists() and xml_path.exists():
            print("\nDownload and extraction completed successfully!")
            print(f"Zip file size: {zip_path.stat().st_size / 1024:.2f} KB")
            print(f"XML file size: {xml_path.stat().st_size / 1024:.2f} KB")
        else:
            print("\nWarning: One or more files are missing after download/extraction")
            
    except requests.exceptions.RequestException as e:
        print(f"Error downloading the file: {e}")
        print("\nTroubleshooting tips:")
        print("1. Check your internet connection")
        print("2. The EU server might be temporarily down - try again in a few minutes")
        print("3. You might need to use a VPN if accessing from outside the EU")
    except zipfile.BadZipFile:
        print("Error: The downloaded file is not a valid zip file")
        if os.path.exists(zip_filename):
            print(f"Deleting invalid zip file: {zip_filename}")
            os.remove(zip_filename)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    download_customs_data() 