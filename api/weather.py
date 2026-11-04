"""Vercel Function: 대한민국 제주도의 현재 날씨를 반환한다."""

from http.server import BaseHTTPRequestHandler
import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


JEJU_COORDINATES = "33.4996,126.5312"


class handler(BaseHTTPRequestHandler):
    def send_json(self, status_code, body):
        payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        api_key = os.environ.get("WEATHER_API_KEY", "").strip()
        if not api_key:
            self.send_json(500, {"message": "WEATHER_API_KEY 환경 변수가 설정되지 않았습니다."})
            return

        query = urlencode({"key": api_key, "q": JEJU_COORDINATES, "lang": "ko"})
        request = Request(
            f"https://api.weatherapi.com/v1/current.json?{query}",
            headers={"Accept": "application/json", "User-Agent": "JejuWeatherApp/1.0"},
        )

        try:
            with urlopen(request, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
            self.send_json(200, data)
        except HTTPError as error:
            try:
                data = json.loads(error.read().decode("utf-8"))
                message = data.get("error", {}).get("message")
            except (json.JSONDecodeError, UnicodeDecodeError):
                message = None
            self.send_json(error.code, {"message": message or "WeatherAPI 요청에 실패했습니다."})
        except (URLError, TimeoutError):
            self.send_json(502, {"message": "날씨 서비스에 연결할 수 없습니다."})
        except (json.JSONDecodeError, UnicodeDecodeError):
            self.send_json(502, {"message": "날씨 서비스의 응답을 해석할 수 없습니다."})

