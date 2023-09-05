# -*- coding: utf-8 -*-
import base64
import os.path
import json,time
import requests
def main(**kargs):
    target_path = os.path.join("data", "qrcode", "keyboard.png")
    ko = os.path.join(os.path.split(os.path.realpath(__file__))[0], "..", "..", "..", "..", "output", "keyboard")
    target_path = 'D:\\Snapshot001.jpg'
    with open(target_path, "rb") as f:
        tk = f.read()
        image = base64.b64encode(tk)
    data = {"image": image.decode("utf-8")}
    #print(data)
    print('Get Keyboard Location')
    # data = json.dumps(m, ensure_ascii=False)
    url = "http://10.176.34.22:58083/"
    resp = requests.post(url+"image/segment?qrcode=3&show=1&name=keyboard&key=G&async=1", json=data)
    json_data = json.loads(resp.text)
    print(json_data)
    getLocation = url+json_data['taskid']
    print(getLocation)
    while True:
        resp1 = requests.get(getLocation)
        print(resp1.status_code)
        if resp1.status_code != 404:
            print(resp1.text)
            break
        time.sleep(30)

if __name__ == "__main__":
    ret = main()
    print(ret)
