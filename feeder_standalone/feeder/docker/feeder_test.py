import requests

def send_data(user_input):
    print(f"{8*'='}REQUEST STARTED{8*'='}")
    res = requests.post('http://localhost', json=user_input)
    print(f"==Client==:{res.request.body}")
    print(f"==Client==:{res.status_code}")
    print(f"==Client==:{res._content}")
    print(f"{8*'='}REQUEST COMPLETED{8*'='}\n")


def main():
    # Send good data
    send_data({"url":"http://google.com"})
    # Send bad format
    send_data({"urls":"http://google.com"})
    # Send bad url
    send_data({"url":"http://idontexist.wtfthesafda"})
    # Send two urls
    send_data({"url":["http://idontexist.wtfthesafda", "http://idontexist.wtfthesafda"]})
    # Send bad type 
    send_data(1)

    
if __name__ == '__main__':
    main()