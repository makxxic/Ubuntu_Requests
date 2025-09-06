import requests
import os
import hashlib
from urllib.parse import urlparse
from pathlib import Path

def get_filename_from_url(url: str) -> str:
    """Extract filename from URL or generate a safe one."""
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)
    
    if not filename or "." not in filename:
        filename = "downloaded_image.jpg"
    return filename

def safe_filename(directory: str, filename: str) -> str:
    """Ensure filename is unique inside directory (avoid duplicates)."""
    filepath = Path(directory) / filename
    if filepath.exists():
        name, ext = os.path.splitext(filename)
        counter = 1
        while True:
            new_filename = f"{name}_{counter}{ext}"
            filepath = Path(directory) / new_filename
            if not filepath.exists():
                return new_filename
            counter += 1
    return filename

def fetch_image(url: str, directory: str = "Fetched_Images") -> None:
    """Download and save an image from a URL with error handling."""
    try:
        # Create directory if missing
        os.makedirs(directory, exist_ok=True)
        
        # Fetch image with timeout
        response = requests.get(url, timeout=10, stream=True)
        response.raise_for_status()  # Raise HTTP errors

        # Security check: only save if content-type is an image
        content_type = response.headers.get("Content-Type", "")
        if not content_type.startswith("image/"):
            print(f"✗ Skipped: {url} (Not an image, got {content_type})")
            return
        
        # Extract and ensure safe filename
        filename = get_filename_from_url(url)
        filename = safe_filename(directory, filename)

        filepath = Path(directory) / filename

        # Avoid duplicates by checking content hash
        file_hash = hashlib.md5(response.content).hexdigest()
        for existing_file in Path(directory).iterdir():
            if existing_file.is_file():
                with open(existing_file, "rb") as f:
                    existing_hash = hashlib.md5(f.read()).hexdigest()
                    if file_hash == existing_hash:
                        print(f"✗ Duplicate skipped: {filename}")
                        return

        # Save image in binary mode
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        print(f"✓ Successfully fetched: {filename}")
        print(f"✓ Image saved to {filepath}")
    
    except requests.exceptions.RequestException as e:
        print(f"✗ Connection error for {url}: {e}")
    except Exception as e:
        print(f"✗ An unexpected error occurred: {e}")

def main():
    print("Welcome to the Ubuntu Image Fetcher")
    print("A tool for mindfully collecting images from the web\n")
    
    urls = input("Please enter image URL(s) (comma-separated): ").split(",")
    urls = [u.strip() for u in urls if u.strip()]
    
    for url in urls:
        fetch_image(url)

    print("\nConnection strengthened. Community enriched.")

if __name__ == "__main__":
    main()
