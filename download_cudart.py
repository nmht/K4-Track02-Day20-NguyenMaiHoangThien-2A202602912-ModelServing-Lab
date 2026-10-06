import urllib.request
import zipfile
import io
import time
import os

url1 = "https://github.com/ggml-org/llama.cpp/releases/download/b10488/llama-b10488-bin-win-cuda-12.4-x64.zip"
url2 = "https://github.com/ggml-org/llama.cpp/releases/download/b10488/cudart-llama-bin-win-cuda-12.4-x64.zip"

def download_and_extract(url, dest):
    print(f"Downloading {url}...")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    data = None
    for i in range(10):
        try:
            data = urllib.request.urlopen(req, timeout=15).read()
            break
        except Exception as e:
            print(f"Attempt {i+1} failed: {e}")
            time.sleep(2)
    
    if data:
        print("Extracting...")
        zipfile.ZipFile(io.BytesIO(data)).extractall(dest)
        print("Done.")
    else:
        print("Failed to download.")

os.makedirs('runtime/b10488', exist_ok=True)
download_and_extract(url1, 'runtime/b10488/')
download_and_extract(url2, 'runtime/b10488/')
