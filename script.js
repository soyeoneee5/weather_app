const elements = {
  loading: document.querySelector("#loading"),
  error: document.querySelector("#error"),
  errorMessage: document.querySelector("#error-message"),
  weather: document.querySelector("#weather"),
  temperature: document.querySelector("#temperature"),
  humidity: document.querySelector("#humidity"),
  conditionText: document.querySelector("#condition-text"),
  conditionIcon: document.querySelector("#condition-icon"),
  lastUpdated: document.querySelector("#last-updated"),
  refreshButton: document.querySelector("#refresh-button"),
};

function setLoading(isLoading) {
  elements.refreshButton.disabled = isLoading;
  elements.refreshButton.classList.toggle("is-loading", isLoading);
  elements.refreshButton.querySelector("span").textContent = isLoading
    ? "불러오는 중"
    : "새로고침";
}

function showError(message) {
  elements.loading.hidden = true;
  elements.weather.hidden = true;
  elements.error.hidden = false;
  elements.errorMessage.textContent = message;
}

function renderWeather(data) {
  const { current } = data;

  elements.temperature.textContent = Math.round(current.temp_c);
  elements.humidity.textContent = current.humidity;
  elements.conditionText.textContent = current.condition.text;
  elements.conditionIcon.src = current.condition.icon.startsWith("//")
    ? `https:${current.condition.icon}`
    : current.condition.icon;
  elements.conditionIcon.alt = `${current.condition.text} 날씨 아이콘`;
  elements.lastUpdated.textContent = current.last_updated;
  elements.lastUpdated.dateTime = current.last_updated.replace(" ", "T");

  elements.loading.hidden = true;
  elements.error.hidden = true;
  elements.weather.hidden = false;
}

async function fetchWeather() {
  setLoading(true);

  try {
    if (window.location.protocol === "file:") {
      throw new Error(
        "HTML 파일을 직접 열 수 없습니다. 터미널에서 python3 server.py를 실행한 뒤 http://127.0.0.1:3000으로 접속해 주세요.",
      );
    }

    const response = await fetch("/api/weather", { cache: "no-store" });
    const responseText = await response.text();
    let data = {};

    if (responseText) {
      try {
        data = JSON.parse(responseText);
      } catch {
        throw new Error(
          "날씨 서버가 올바르지 않은 응답을 보냈습니다. python3 server.py로 실행했는지 확인해 주세요.",
        );
      }
    }

    if (!response.ok) {
      const serverHint =
        response.status === 404
          ? "전용 서버가 아닌 것 같습니다. python3 server.py를 실행한 뒤 http://127.0.0.1:3000으로 접속해 주세요."
          : "날씨 서버에서 오류가 발생했습니다.";
      throw new Error(data.message || serverHint);
    }

    if (!data.current) {
      throw new Error("날씨 데이터가 비어 있습니다. 잠시 후 다시 시도해 주세요.");
    }

    renderWeather(data);
  } catch (error) {
    const message =
      error instanceof TypeError
        ? "서버에 연결할 수 없습니다. 실행 방법을 확인해 주세요."
        : error.message;
    showError(message);
  } finally {
    setLoading(false);
  }
}

elements.refreshButton.addEventListener("click", fetchWeather);
window.addEventListener("DOMContentLoaded", fetchWeather);
