import requests
import os

def download_simple_logo():
    """Download a simple blue logo from a reliable source."""
    # Create a simple colored rectangle as a placeholder logo
    logo_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Logo_TV_2015.svg/1200px-Logo_TV_2015.svg.png"
    
    # Ensure directory exists
    os.makedirs("app/static/images", exist_ok=True)
    
    # Download the logo
    response = requests.get(logo_url)
    
    if response.status_code == 200:
        with open("app/static/images/inkstitchpress_logo.png", "wb") as f:
            f.write(response.content)
        print("Logo downloaded successfully.")
    else:
        print(f"Failed to download logo. Status code: {response.status_code}")

if __name__ == "__main__":
    download_simple_logo() 