import requests

url = "http://localhost:8000/api/v1/summarize"
payload = {
    "url": "https://www.bbc.com/news/articles/cz905eyjznno",
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
        print("\nSentiment:")
        print(f"{data['sentiment']['label']} (Score: {data['sentiment']['score']})")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Connection failed: {e}")
