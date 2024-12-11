import requests

url = "http://localhost:8080/data/transactions"

data = {
  "id": 0,
  "user_id": 0,
  "amount": 0,
  "timestamp": "2024-08-19T04:41:10.501Z"
}

response = requests.post(url, json=data)
print(response.json())


