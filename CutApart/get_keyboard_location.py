import requests,json,time

def GetKeyboardLocation(data_image,code,jsonFileName):
    url = "http://10.119.96.106:58083/"
    data = {"image": data_image.decode("utf-8")}
    print('{} Get Keyboard Location'.format(code))
    resp = requests.post(url+"image/segment?code={}&keyboard=1&show=1&name=keyboard&async=1".format(code), json=data)
    print("Request url is " + str(resp))
    json_data = json.loads(resp.text)
    getLocation = url+json_data['taskid']
    print(getLocation)
    while True:
        resp1 = requests.get(getLocation)
        print(resp1.status_code)
        if resp1.status_code != 404:
            print(resp1.text)
            with open('data_{}_temp.json'.format(code), 'w') as f:
                f.write(resp1.text)
            print("Finished")
            break
        time.sleep(5)