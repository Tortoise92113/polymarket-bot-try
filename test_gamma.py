import requests

url = "https://gamma-api.polymarket.com/markets?active=true&limit=200"
r = requests.get(url)

print("Status:", r.status_code)
print(r.json())
