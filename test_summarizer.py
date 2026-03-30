import requests

url = "http://localhost:8000/api/v1/summarize"
payload = {
    "url": "https://timesofindia.indiatimes.com/city/visakhapatnam/visakhapatnam-horror-navy-technician-kills-woman-dismembers-body-stores-parts-in-fridge/articleshow/129889816.cms",
    "length": "medium"
}

try:
    response = requests.post(url, json=payload, timeout=60)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("Summary Paragraph:")
        print(data["summary_paragraph"])
        print("\nSummary Bullets:")
        for bullet in data["summary_bullets"]:
            print(f"- {bullet}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Connection failed: {e}")
