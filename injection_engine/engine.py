import requests
from urllib.parse import quote

def send_get_request(url, payload):
    params = None
    if "INJ" in url:
        injected_url = url.replace("INJ", quote(payload))
    else:
        injected_url = url
        params = {'q': payload}

    try:
        response = requests.get(injected_url)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error sending request: {e}")
        return None
    
if __name__ == '__main__':
    from payload_generator.generator import generate_basic_payload
    
    testURL = "http://127.0.0.1/?q=INJ"
    basic_payload = generate_basic_payload()
    
    print(f"Testing with URL: {testURL}")
    print(f"Sending payload: {basic_payload}")
    
    response = send_get_request(testURL, basic_payload)
    
    if response:
        print(f"Response status code: {response.status_code}")
        print(f"URL sent: {response.url}")