def check_if_allowed(url, tag):
    from injection_engine.engine import send_get_request
    probe_payload = f"<{tag}>"
    response = send_get_request(url, probe_payload)
    if response is None:
        return False
    return response.status_code < 400

def analyze_response(response, payload):
    if response is None:
        return "blocked", "No response received (error)"
    status_code = response.status_code
    if status_code < 400:
        return "bypassed", f"Potential bypass: Received status code {status_code}"
    else:
        return "blocked", f"Blocked: Received status code {status_code}"

if __name__ == '__main__':
    import argparse
    from injection_engine.engine import send_get_request
    from payload_generator.generator import generate_basic_payload
    parser = argparse.ArgumentParser(description="Example for response_analyzer.")
    parser.add_argument("url", nargs='?', default="http://127.0.0.1/?q=INJ", help="The target URL with 'INJ' as a placeholder for the payload.")
    args = parser.parse_args()
    testURL = args.url
    test_payload = generate_basic_payload()
    if "INJ" not in testURL:
        print("Error: The example URL must contain the 'INJ' placeholder.")
    else:
        print(f"Testing with URL: {testURL}")
        print(f"Sending payload: {test_payload}")
        res = send_get_request(testURL, test_payload)
        status, reason = analyze_response(res, test_payload)
        print(f"Analysis result: {status} - {reason}")
        if res:
            print(f"URL sent: {res.url}")