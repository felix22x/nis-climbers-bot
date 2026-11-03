import httpx

for url in [
    "https://api.telegram.org",
    "https://www.google.com",
]:
    try:
        response = httpx.get(url, timeout=15)
        print(f"{url}: HTTP {response.status_code}", flush=True)
    except Exception as e:
        print(f"{url}: {type(e).__name__}: {e}", flush=True)
