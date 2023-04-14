import re, subprocess

def normalize_url(url):
    url_upper = url.upper()
    if 'HTTPS://' in url_upper:
        return ((url_upper.replace('HTTPS://', '')).replace('WWW.', ''), 'HTTPS://')
    else:
        return ((url_upper.replace('HTTP://', '')).replace('WWW.', ''), 'HTTP://')

def get_network_stats(url):
    ipv4_pattern = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
    normalized_url, _ = normalize_url(url)
    splited_url = normalized_url.split('.')
    counter = 2
    while True:
        shift_list = splited_url[-1:-counter:-1][-1::-1]
        shift_url = '.'.join(shift_list)
        response = subprocess.run(['nslookup', shift_url], capture_output=True)
        ipv4 = ipv4_pattern.findall(response.stdout.decode('utf-8'))[-1]
        if response.returncode == 0 and "127.0.0" not in ipv4:
            return shift_list[0], ipv4, True
        if counter >= 6:
            return _, _, False
        counter = counter + 1

def main():
    get_network_stats('MAPS.GOOGLE.CO.IL')

if __name__ == "__main__":
    main()
