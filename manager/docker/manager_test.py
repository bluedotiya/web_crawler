import requests

MANAGER_DNS_NAME = "localhost"

def send_data(user_input):
    print(f"{8*'='}REQUEST STARTED{8*'='}")
    res = requests.post(f"http://{MANAGER_DNS_NAME}", json=user_input)
    print(f"==Client==:{res.request.body}")
    print(f"==Client==:{res.status_code}")
    print(f"==Client==:{res._content}")
    print(f"{8*'='}REQUEST COMPLETED{8*'='}\n")


def main():
    # Send good data
    send_data({"url":"http://google.com", "depth":2})
    # Send bad format
    send_data({"urls":"http://google.com"})
    # Send bad url
    send_data({"url":"http://idontexist.wtfthesafda"})
    # Send two urls
    send_data({"url":["http://idontexist.wtfthesafda", "http://idontexist.wtfthesafda"]})
    # Send bad type 
    send_data(1)
    # Send no depth
    send_data({"url":"http://google.com"})
    
    
if __name__ == '__main__':
    main()