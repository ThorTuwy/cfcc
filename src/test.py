import requests

url = "http://localhost:8191/v1"
headers = {"Content-Type": "application/json"}
data = {
    "cmd": "request.get",
    "tabs_till_verify":1,
    "waitInSeconds":3,
    "url": "https://codeforces.com/enter",
    "maxTimeout": 3000000,
    "returnScreenshot":True
}
response = requests.post(url, headers=headers, json=data)
print(response.text)