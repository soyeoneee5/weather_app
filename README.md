# 지금 제주 날씨는?

WeatherAPI.com의 `current.json`을 사용해 대한민국 제주도의 현재 기온, 습도, 날씨 설명, 데이터 업데이트 시각을 보여주는 간단한 웹앱입니다.

## 실행 방법

```bash
python3 server.py
```

브라우저에서 <http://127.0.0.1:3000>을 여세요.

서버는 프로젝트 폴더에서 이름이 `apikey.txt`로 끝나는 파일의 API 키를 읽습니다. 또는 환경 변수 `WEATHER_API_KEY`로 전달할 수도 있습니다.

## Vercel 배포

1. 이 GitHub 저장소를 Vercel 프로젝트로 가져옵니다.
2. Vercel 프로젝트의 **Settings → Environment Variables**에서 다음 값을 추가합니다.
   - 이름: `WEATHER_API_KEY`
   - 값: WeatherAPI.com API 키
3. Production, Preview, Development 중 필요한 환경을 선택하고 배포합니다.

Vercel에서는 [`api/weather.py`](api/weather.py)가 `/api/weather` 서버리스 함수로 실행됩니다. API 키는 서버에서만 사용되며 브라우저 코드와 GitHub 저장소에는 포함되지 않습니다.

## 보안

API 키는 브라우저에 전달되지 않습니다. `*apikey.txt`와 `.env`는 `.gitignore`에 포함되어 있으므로 GitHub에 커밋되지 않습니다.
