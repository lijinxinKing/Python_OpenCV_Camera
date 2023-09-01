import requests
import json
url = "https://songguoyun.topwd.top/Esp_Api_new.php"
payload = "%7B%0A%20%20%20%20%22sgdz_account%22%3A%20%22autotest%22%2C%0A%20%20%20%20%22sgdz_password%22%3A%20%22123qwe123%22%2C%0A%20%20%20%20%22device_name%22%3A%20%22autotest%22%2C%0A%20%20%20%20%22value%22%3A%20%2214%22%0A%7D"
headers = {
  'Content-Type': 'application/json'
}
response = requests.request("POST", url, headers=headers, data=payload)
print(response.text)
