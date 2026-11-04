"""제주 날씨 앱의 정적 파일과 WeatherAPI 프록시를 제공하는 로컬 서버."""

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen


HOST = "127.0.0.1"
PORT = int(os.environ.get("PORT", "3000"))
ROOT = Path(__file__).resolve().parent
PUBLIC_FILES = {"/", "/index.html", "/style.css", "/script.js"}


def read_api_key():
    """환경 변수 또는 프로젝트 내 apikey.txt 파일에서 키를 읽는다."""
    environment_key = os.environ.get("WEATHER_API_KEY", "").strip()
    if environment_key:
        return environment_key

    key_files = list(ROOT.glob("*apikey.txt"))
    if not key_files:
        raise FileNotFoundError("날씨 API 키 파일을 찾을 수 없습니다.")

    api_key = key_files[0].read_text(encoding="utf-8").strip()
    if not api_key:
        raise ValueError("WeatherAPI 키가 비어 있습니다.")
    return api_key


class WeatherHandler(SimpleHTTPRequestHandler):
    """WeatherAPI 키를 브라우저에 노출하지 않는 요청 처리기."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def send_json(self, status_code, body):
        payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(payload)

    def serve_weather(self):
        try:
            # "Jeju"라는 이름의 다른 지역으로 잘못 매칭되지 않도록
            # 대한민국 제주시청 인근 좌표를 사용한다.
            query = urlencode(
                {"key": read_api_key(), "q": "33.4996,126.5312", "lang": "ko"}
            )
            request = Request(
                f"https://api.weatherapi.com/v1/current.json?{query}",
                headers={"Accept": "application/json", "User-Agent": "JejuWeatherApp/1.0"},
            )

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
        except (FileNotFoundError, ValueError) as error:
            self.send_json(500, {"message": str(error)})
        except (URLError, TimeoutError):
            self.send_json(502, {"message": "날씨 서비스에 연결할 수 없습니다."})
        except (json.JSONDecodeError, UnicodeDecodeError):
            self.send_json(502, {"message": "날씨 서비스의 응답을 해석할 수 없습니다."})

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/weather":
            self.serve_weather()
            return
        if path not in PUBLIC_FILES:
            self.send_error(404, "Not found")
            return

        self.path = "/index.html" if path == "/" else path
        super().do_GET()

    def end_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        super().end_headers()


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), WeatherHandler)
    print(f"제주 날씨 앱: http://{HOST}:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n서버를 종료합니다.")
    finally:
        server.server_close()
