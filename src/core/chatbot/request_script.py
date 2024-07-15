import requests

url = "http://127.0.0.1:62384/api/query-v3/"
params = {
    "query_text": "YOUR_QUERY_HERE",
    "num_results": 5
}

try:
    response = requests.get(url, params=params)
    response.raise_for_status()  # HTTP 에러가 발생하면 예외를 발생시킵니다.
    data = response.json()  # JSON 파싱 시도
    print(data)
except requests.exceptions.HTTPError as errh:
    print(f"HTTP Error: {errh}")
except requests.exceptions.ConnectionError as errc:
    print(f"Error Connecting: {errc}")
except requests.exceptions.Timeout as errt:
    print(f"Timeout Error: {errt}")
except requests.exceptions.RequestException as err:
    print(f"Request Error: {err}")
except ValueError as e:  # JSONDecodeError는 ValueError의 하위 클래스입니다.
    print(f"JSON Decode Error: {e}")
