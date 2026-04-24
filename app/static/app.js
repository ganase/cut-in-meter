// ── DOM 参照 ─────────────────────────────────────────────
const startCameraButton    = document.querySelector("#startCameraButton");
const stopCameraButton     = document.querySelector("#stopCameraButton");
const captureButton        = document.querySelector("#captureButton");
const analyzeButton        = document.querySelector("#analyzeButton");
const autoAnalyzeButton    = document.querySelector("#autoAnalyzeButton");
const manualSignalButtons  = document.querySelectorAll("[data-manual-signal]");
const autoAnalyzeIntervalInput = document.querySelector("#autoAnalyzeIntervalInput");
const judgmentLevelSelect  = document.querySelector("#judgmentLevelSelect");
const deviceNameInput      = document.querySelector("#deviceNameInput");
const fileInput            = document.querySelector("#fileInput");
const cameraPreview        = document.querySelector("#cameraPreview");
const uploadVideo          = document.querySelector("#uploadVideo");
const imagePreview         = document.querySelector("#imagePreview");
const emptyPreview         = document.querySelector("#emptyPreview");
const sourceLabel          = document.querySelector("#sourceLabel");
const videoScrubberWrap    = document.querySelector("#videoScrubberWrap");
const videoScrubber        = document.querySelector("#videoScrubber");
const trafficLight         = document.querySelector("#trafficLight");
const scoreValue           = document.querySelector("#scoreValue");
const confidenceValue      = document.querySelector("#confidenceValue");
const processingStateValue = document.querySelector("#processingStateValue");
const nextAnalyzeValue     = document.querySelector("#nextAnalyzeValue");
const reasons              = document.querySelector("#reasons");
const playfulSuggestion    = document.querySelector("#playfulSuggestion");
const statusMessage        = document.querySelector("#statusMessage");
const workingCanvas        = document.querySelector("#workingCanvas");
const snapshotPanel        = document.querySelector("#snapshotPanel");
const snapshotPreview      = document.querySelector("#snapshotPreview");
const scoreChartCanvas     = document.querySelector("#scoreChart");
const chartDateLabel       = document.querySelector("#chartDateLabel");

// 新規: ヘッダー・テーマ・最小化・ミニウィジェット
const minimizeButton = document.querySelector("#minimizeButton");
const restoreButton  = document.querySelector("#restoreButton");
const themeButton    = document.querySelector("#themeButton");
const themeIcon      = document.querySelector("#themeIcon");
const miniWidget     = document.querySelector("#miniWidget");
const miniDot        = document.querySelector("#miniDot");
const miniScore      = document.querySelector("#miniScore");
const miniHl         = document.querySelector("#miniHl");
const logoSignal     = document.querySelector("#logoSignal");

// ── 定数 ──────────────────────────────────────────────────
const AUTO_ANALYZE_DEFAULT_SECONDS = 10;
const AUTO_ANALYZE_MIN_SECONDS = 2;
const CAPTURE_MAX_SIDE = 320;
const CAPTURE_JPEG_QUALITY = 0.66;

const JUDGMENT_LEVEL_LABELS = {
  strict:   "慎重",
  balanced: "標準",
  lenient:  "ゆるめ",
};

const MANUAL_SIGNAL_CONTENT = {
  red: {
    label: "赤",
    headline: "今はそっとしておきましょう",
    reasons: ["手動で赤信号に切り替えました"],
    playfulSuggestion: "あとで声をかける前提で、今はいったん待機です。",
  },
  yellow: {
    label: "黄",
    headline: "様子を見ながらが安全です",
    reasons: ["手動で黄信号に切り替えました"],
    playfulSuggestion: "ひと呼吸おいて、短めに声をかける想定です。",
  },
  blue: {
    label: "青",
    headline: "今なら話しかけてよさそうです",
    reasons: ["手動で青信号に切り替えました"],
    playfulSuggestion: "軽く一言だけ、テンポよく話しかけましょう。",
  },
};

// ── テーマ ────────────────────────────────────────────────

const THEMES = ["warm", "dark", "cool"];

const THEME_ICONS = {
  warm: `<circle cx="8" cy="8" r="3" fill="currentColor"/>
         <path d="M8 1v2M8 13v2M1 8h2M13 8h2M3.22 3.22l1.42 1.42M11.36 11.36l1.42 1.42M11.36 4.64l1.42-1.42M3.22 12.78l1.42-1.42"
               stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>`,
  dark: `<path d="M13.5 10.5A6 6 0 1 1 5.5 2.5a4.5 4.5 0 0 0 8 8z"
               fill="currentColor"/>`,
  cool: `<path d="M8 1v14M1 8h14M3.1 3.1l9.8 9.8M12.9 3.1 3.1 12.9"
               stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>`,
};

function getCurrentTheme() {
  return document.documentElement.dataset.theme || "warm";
}

function applyTheme(theme) {
  document.documentElement.dataset.theme = theme;
  localStorage.setItem("cutInMeterTheme", theme);
  themeIcon.innerHTML = THEME_ICONS[theme];
}

function cycleTheme() {
  const current = getCurrentTheme();
  const idx = THEMES.indexOf(current);
  applyTheme(THEMES[(idx + 1) % THEMES.length]);
}

function initTheme() {
  const saved = localStorage.getItem("cutInMeterTheme");
  applyTheme(THEMES.includes(saved) ? saved : "warm");
}

themeButton.addEventListener("click", cycleTheme);

// ── 最小化 ────────────────────────────────────────────────

function minimize() {
  document.documentElement.classList.add("minimized");
  miniWidget.hidden = false;
}

function restore() {
  document.documentElement.classList.remove("minimized");
  miniWidget.hidden = true;
}

minimizeButton.addEventListener("click", minimize);
restoreButton.addEventListener("click", restore);

// ── シグナル同期（ヘッダードット + ミニウィジェット） ────

function syncSignalUI(signal, scoreText, headlineText) {
  // ヘッダーのロゴドット
  logoSignal.dataset.signal = signal || "";

  // スコア値の色
  const colorMap = {
    red:    "var(--red)",
    yellow: "var(--yellow)",
    blue:   "var(--blue)",
  };
  scoreValue.style.color = colorMap[signal] || "";

  // ミニウィジェット
  miniDot.dataset.signal  = signal || "";
  miniScore.textContent   = scoreText  ?? "--";
  miniHl.textContent      = headlineText ?? "判定待ち";
}

// ── デバイス名管理 ────────────────────────────────────────

function getDeviceName() {
  return deviceNameInput.value.trim() || "PC";
}

function initDeviceName() {
  let name = localStorage.getItem("cutInMeterDeviceName");
  if (!name) {
    const rand = Math.random().toString(36).slice(2, 10).toUpperCase();
    name = `PC-${rand}`;
    localStorage.setItem("cutInMeterDeviceName", name);
  }
  deviceNameInput.value = name;
}

deviceNameInput.addEventListener("change", () => {
  const name = deviceNameInput.value.trim();
  if (name) localStorage.setItem("cutInMeterDeviceName", name);
});

// ── チャート ──────────────────────────────────────────────

function scoreToColor(score) {
  if (score >= 60) return "#1878c8";
  if (score >= 25) return "#c9900d";
  return "#c83030";
}

let scoreHistory = [];
let scoreChart = null;

function initChart() {
  const ctx = scoreChartCanvas.getContext("2d");
  scoreChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: [],
      datasets: [{
        label: "分平均スコア",
        data: [],
        borderColor: "#0f766e",
        backgroundColor: "rgba(15, 118, 110, 0.07)",
        tension: 0.4,
        fill: true,
        pointBackgroundColor: [],
        pointRadius: 3,
        pointHoverRadius: 5,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          min: 0,
          max: 100,
          grid: { color: "rgba(128,128,128,0.10)" },
          ticks: {
            font: { family: "IBM Plex Sans", size: 11 },
            color: "#888",
            stepSize: 25,
          },
        },
        x: {
          grid: { color: "rgba(128,128,128,0.10)" },
          ticks: {
            font: { family: "IBM Plex Sans", size: 11 },
            color: "#888",
            maxRotation: 0,
          },
        },
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: { label: (ctx) => `スコア: ${ctx.parsed.y}` },
        },
      },
      animation: { duration: 300 },
    },
  });

  const today = new Date();
  chartDateLabel.textContent =
    `${today.getFullYear()}/${today.getMonth() + 1}/${today.getDate()}`;
}

function computeMinuteAverages() {
  const buckets = {};
  for (const { timestamp, score } of scoreHistory) {
    const dt = new Date(timestamp);
    const key = `${String(dt.getHours()).padStart(2, "0")}:${String(dt.getMinutes()).padStart(2, "0")}`;
    if (!buckets[key]) buckets[key] = [];
    buckets[key].push(score);
  }
  return Object.entries(buckets)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([minute, scores]) => ({
      minute,
      avgScore: Math.round((scores.reduce((a, b) => a + b, 0) / scores.length) * 10) / 10,
    }));
}

function refreshChart() {
  if (!scoreChart) return;
  const data = computeMinuteAverages();
  scoreChart.data.labels = data.map((d) => d.minute);
  scoreChart.data.datasets[0].data = data.map((d) => d.avgScore);
  scoreChart.data.datasets[0].pointBackgroundColor = data.map((d) => scoreToColor(d.avgScore));
  scoreChart.update();
}

async function loadTodayHistory() {
  const today = new Date().toISOString().slice(0, 10);
  try {
    const res = await fetch(`/api/stats?date=${today}`);
    if (!res.ok) return;
    const { records } = await res.json();
    scoreHistory = records.map((r) => ({ timestamp: r.timestamp, score: Number(r.score) }));
    refreshChart();
  } catch (e) {
    console.warn("履歴の読み込みに失敗しました", e);
  }
}

// ── 共通ユーティリティ ────────────────────────────────────

let cameraStream = null;
let currentSource = null;
let autoAnalyzeTimer = null;
let autoAnalyzeCountdownTimer = null;
let analyzeInFlight = false;
let nextAutoAnalyzeAtMs = null;

function releaseCurrentObjectUrl() {
  if (currentSource?.objectUrl) URL.revokeObjectURL(currentSource.objectUrl);
}

function setStatus(message) { statusMessage.textContent = message; }
function setSource(name)  { sourceLabel.textContent = name; }

function hideAllMedia() {
  cameraPreview.classList.add("hidden");
  uploadVideo.classList.add("hidden");
  imagePreview.classList.add("hidden");
  emptyPreview.classList.add("hidden");
}

function canAutoAnalyze() { return currentSource?.kind === "camera"; }

function syncAnalyzeControls() {
  analyzeButton.disabled = !currentSource;
  autoAnalyzeButton.disabled = !canAutoAnalyze();
  autoAnalyzeButton.textContent =
    autoAnalyzeTimer === null ? "自動判定を開始" : "自動判定を停止";
}

function currentJudgmentLevel() {
  return judgmentLevelSelect.value in JUDGMENT_LEVEL_LABELS
    ? judgmentLevelSelect.value
    : "balanced";
}

function currentJudgmentLevelLabel() {
  return JUDGMENT_LEVEL_LABELS[currentJudgmentLevel()];
}

function clearAutoAnalyzeCountdownTimer() {
  if (autoAnalyzeCountdownTimer !== null) {
    window.clearInterval(autoAnalyzeCountdownTimer);
    autoAnalyzeCountdownTimer = null;
  }
}

function formatCountdown(targetMs) {
  const seconds = Math.ceil(Math.max(0, targetMs - Date.now()) / 1000);
  return `${seconds}秒`;
}

function renderNextAnalyzeCountdown() {
  if (autoAnalyzeTimer === null || nextAutoAnalyzeAtMs === null) {
    nextAnalyzeValue.textContent = "--";
    return;
  }
  nextAnalyzeValue.textContent = analyzeInFlight ? "判定中" : formatCountdown(nextAutoAnalyzeAtMs);
}

function setProcessingState(label) { processingStateValue.textContent = label; }

function setNextAutoAnalyzeTimestamp(timestampMs) {
  nextAutoAnalyzeAtMs =
    typeof timestampMs === "number" && Number.isFinite(timestampMs) ? timestampMs : null;
  clearAutoAnalyzeCountdownTimer();
  renderNextAnalyzeCountdown();
  if (nextAutoAnalyzeAtMs !== null) {
    autoAnalyzeCountdownTimer = window.setInterval(renderNextAnalyzeCountdown, 1000);
  }
}

function showSnapshot(imageDataUrl) {
  snapshotPreview.src = imageDataUrl;
  snapshotPanel.classList.remove("hidden");
}

function clearSnapshot() {
  snapshotPreview.removeAttribute("src");
  snapshotPanel.classList.add("hidden");
}

function setReasons(items) {
  reasons.replaceChildren(
    ...items.map((item) => {
      const li = document.createElement("li");
      li.textContent = item;
      return li;
    }),
  );
}

function setManualSignal(signal) {
  const content = MANUAL_SIGNAL_CONTENT[signal];
  if (!content) return;

  stopAutoAnalyze();
  trafficLight.dataset.signal = signal;
  scoreValue.textContent = "--";
  confidenceValue.textContent = "--";
  setReasons(content.reasons);
  playfulSuggestion.textContent = content.playfulSuggestion;
  clearSnapshot();
  setProcessingState("手動設定");
  setStatus(`手動で${content.label}信号に切り替えました。`);

  // ヘッダー・ミニウィジェット同期
  syncSignalUI(signal, "--", content.headline);
}

function showEmptyState() {
  stopAutoAnalyze();
  releaseCurrentObjectUrl();
  hideAllMedia();
  emptyPreview.classList.remove("hidden");
  videoScrubberWrap.classList.add("hidden");
  currentSource = null;
  startCameraButton.disabled = false;
  captureButton.disabled = true;
  stopCameraButton.disabled = true;
  setSource("ソース未選択");
  clearSnapshot();
  setProcessingState("待機中");
  setNextAutoAnalyzeTimestamp(null);
  syncAnalyzeControls();
}

function normalizeAutoAnalyzeSeconds() {
  const rawValue = Number(autoAnalyzeIntervalInput.value);
  const safeValue = Number.isFinite(rawValue) ? rawValue : AUTO_ANALYZE_DEFAULT_SECONDS;
  const normalizedValue = Math.max(AUTO_ANALYZE_MIN_SECONDS, Math.round(safeValue));
  autoAnalyzeIntervalInput.value = String(normalizedValue);
  return normalizedValue;
}

function stopAutoAnalyze() {
  if (autoAnalyzeTimer !== null) {
    window.clearInterval(autoAnalyzeTimer);
    autoAnalyzeTimer = null;
  }
  setNextAutoAnalyzeTimestamp(null);
  syncAnalyzeControls();
}

function startAutoAnalyzeInterval() {
  if (!canAutoAnalyze()) { stopAutoAnalyze(); return; }
  stopAutoAnalyze();
  const seconds = normalizeAutoAnalyzeSeconds();
  autoAnalyzeTimer = window.setInterval(() => {
    setNextAutoAnalyzeTimestamp(Date.now() + seconds * 1000);
    void analyzeCurrentFrame({ silentIfBusy: true });
  }, seconds * 1000);
  setNextAutoAnalyzeTimestamp(Date.now() + seconds * 1000);
  syncAnalyzeControls();
}

function stopCamera() {
  if (cameraStream) {
    for (const track of cameraStream.getTracks()) track.stop();
    cameraStream = null;
  }
  cameraPreview.srcObject = null;
  stopAutoAnalyze();
  if (!currentSource || currentSource.kind === "camera") {
    showEmptyState();
  } else {
    startCameraButton.disabled = false;
    stopCameraButton.disabled = true;
    captureButton.disabled = true;
  }
}

async function requestCameraStream() {
  if (!navigator.mediaDevices?.getUserMedia)
    throw new DOMException("getUserMedia is not available.", "NotSupportedError");
  try {
    return await navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" }, audio: false });
  } catch (error) {
    if (error.name !== "OverconstrainedError" && error.name !== "ConstraintNotSatisfiedError") throw error;
    return navigator.mediaDevices.getUserMedia({ video: true, audio: false });
  }
}

function cameraErrorMessage(error) {
  if (!window.isSecureContext || !navigator.mediaDevices?.getUserMedia)
    return "カメラを開始できませんでした。http://127.0.0.1:8000、http://localhost:8000、または https のページで開いてください。";
  switch (error.name) {
    case "NotAllowedError":
    case "SecurityError":
      return "カメラを開始できませんでした。ブラウザまたはOSのカメラ権限が拒否されています。";
    case "NotFoundError":
    case "DevicesNotFoundError":
      return "カメラを開始できませんでした。利用できるカメラが見つかりません。";
    case "NotReadableError":
    case "TrackStartError":
      return "カメラを開始できませんでした。他のアプリがカメラを使用中の可能性があります。";
    default:
      return `カメラを開始できませんでした。${error.name || "UnknownError"}: ${error.message || "権限設定を確認してください。"}`;
  }
}

async function startCamera() {
  setProcessingState("カメラ起動中");
  setStatus("カメラを起動しています...");
  startCameraButton.disabled = true;
  try {
    stopCamera();
    setProcessingState("カメラ起動中");
    setStatus("カメラを起動しています...");
    const stream = await requestCameraStream();
    cameraStream = stream;
    hideAllMedia();
    cameraPreview.classList.remove("hidden");
    cameraPreview.srcObject = stream;
    currentSource = { kind: "camera" };
    setSource("ライブカメラ");
    stopCameraButton.disabled = false;
    captureButton.disabled = false;
    syncAnalyzeControls();
    setProcessingState("カメラ待機");
    setStatus("カメラの準備ができました。AIで判定を押すと自動更新が始まります。");
  } catch (error) {
    console.error(error);
    startCameraButton.disabled = false;
    setProcessingState("カメラ失敗");
    setStatus(cameraErrorMessage(error));
  }
}

function drawMediaToCanvas(element) {
  const context = workingCanvas.getContext("2d");
  const sourceWidth  = element.videoWidth  || element.naturalWidth  || element.width;
  const sourceHeight = element.videoHeight || element.naturalHeight || element.height;
  const scale = Math.min(1, CAPTURE_MAX_SIDE / Math.max(sourceWidth, sourceHeight));
  workingCanvas.width  = Math.max(1, Math.round(sourceWidth  * scale));
  workingCanvas.height = Math.max(1, Math.round(sourceHeight * scale));
  context.drawImage(element, 0, 0, workingCanvas.width, workingCanvas.height);
  return workingCanvas.toDataURL("image/jpeg", CAPTURE_JPEG_QUALITY);
}

async function captureCurrentFrame() {
  if (!currentSource) return null;
  if (currentSource.kind === "camera")       return drawMediaToCanvas(cameraPreview);
  if (currentSource.kind === "upload-image") return drawMediaToCanvas(imagePreview);
  if (currentSource.kind === "upload-video") return drawMediaToCanvas(uploadVideo);
  return null;
}

function updateResult(result) {
  trafficLight.dataset.signal = result.signal;
  scoreValue.textContent      = String(result.score);
  confidenceValue.textContent = `${result.confidence}%`;
  setReasons(result.reasons);
  playfulSuggestion.textContent = result.playfulSuggestion;
  setProcessingState("結果を反映");

  // ヘッダー・ミニウィジェット同期
  syncSignalUI(result.signal, String(result.score), result.headline);
}

async function analyzeCurrentFrame(options = {}) {
  const { silentIfBusy = false } = options;
  if (analyzeInFlight) {
    if (!silentIfBusy) setStatus("現在の判定が終わるまでお待ちください。");
    return;
  }

  setProcessingState("フレーム取得中");
  const imageDataUrl = await captureCurrentFrame();
  if (!imageDataUrl) {
    setProcessingState("待機中");
    setStatus("先にカメラまたはファイルを選択してください。");
    return;
  }
  showSnapshot(imageDataUrl);

  analyzeInFlight = true;
  analyzeButton.disabled = true;
  renderNextAnalyzeCountdown();
  setProcessingState("AIに送信中");
  setStatus("AIが判定中です...");

  try {
    const response = await fetch("/api/score", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        imageDataUrl,
        sourceLabel: sourceLabel.textContent,
        judgmentLevel: currentJudgmentLevel(),
        deviceName: getDeviceName(),
      }),
    });
    setProcessingState("応答を確認中");
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || "Unknown API error");
    updateResult(payload);
    setStatus(`${payload.model} が${currentJudgmentLevelLabel()}で判定しました。`);

    const ts = payload.generatedAt || new Date().toISOString();
    scoreHistory.push({ timestamp: ts, score: payload.score });
    refreshChart();
  } catch (error) {
    console.error(error);
    setProcessingState("失敗");
    setStatus(`判定に失敗しました: ${error.message}`);
  } finally {
    analyzeInFlight = false;
    setProcessingState(autoAnalyzeTimer === null ? "判定完了" : "自動判定待ち");
    renderNextAnalyzeCountdown();
    syncAnalyzeControls();
  }
}

function onVideoScrub() {
  if (!uploadVideo.duration || Number.isNaN(uploadVideo.duration)) return;
  uploadVideo.currentTime = Number(videoScrubber.value) * uploadVideo.duration;
}

async function loadFile(file) {
  stopAutoAnalyze();
  releaseCurrentObjectUrl();
  clearSnapshot();
  if (!file) { showEmptyState(); return; }
  const url = URL.createObjectURL(file);

  if (file.type.startsWith("image/")) {
    hideAllMedia();
    imagePreview.src = url;
    imagePreview.classList.remove("hidden");
    currentSource = { kind: "upload-image", objectUrl: url };
    captureButton.disabled = true;
    stopCameraButton.disabled = true;
    videoScrubberWrap.classList.add("hidden");
    setSource(`画像ファイル: ${file.name}`);
    syncAnalyzeControls();
    setProcessingState("画像読み込み中");
    setStatus("画像を読み込み中です...");
    return;
  }

  if (file.type.startsWith("video/")) {
    hideAllMedia();
    uploadVideo.src = url;
    uploadVideo.classList.remove("hidden");
    currentSource = { kind: "upload-video", objectUrl: url };
    captureButton.disabled = true;
    stopCameraButton.disabled = true;
    videoScrubberWrap.classList.remove("hidden");
    setSource(`動画ファイル: ${file.name}`);
    syncAnalyzeControls();
    setProcessingState("動画読み込み中");
    setStatus("動画を読み込み中です...");
    return;
  }

  currentSource = null;
  syncAnalyzeControls();
  setProcessingState("待機中");
  setStatus("未対応のファイル形式です。画像か動画を選択してください。");
}

// ── イベントリスナー ──────────────────────────────────────

startCameraButton.addEventListener("click", startCamera);

stopCameraButton.addEventListener("click", async () => {
  const wasAutoAnalyzing = autoAnalyzeTimer !== null;
  if (cameraStream) {
    for (const track of cameraStream.getTracks()) track.stop();
    cameraStream = null;
  }
  cameraPreview.srcObject = null;
  stopAutoAnalyze();
  await startCamera();
  if (wasAutoAnalyzing) {
    startAutoAnalyzeInterval();
    void analyzeCurrentFrame({ silentIfBusy: true });
  }
});

captureButton.addEventListener("click", async () => {
  if (!cameraStream) return;
  stopAutoAnalyze();
  const snapshot = await captureCurrentFrame();
  hideAllMedia();
  imagePreview.src = snapshot;
  imagePreview.classList.remove("hidden");
  currentSource = { kind: "upload-image", dataUrl: snapshot };
  captureButton.disabled = true;
  stopCameraButton.disabled = false;
  setSource("カメラ静止画");
  clearSnapshot();
  syncAnalyzeControls();
  setProcessingState("静止画固定");
  setStatus("カメラ映像を静止画として固定しました。");
});

analyzeButton.addEventListener("click", () => {
  if (canAutoAnalyze()) {
    startAutoAnalyzeInterval();
    setStatus(`自動判定中です。${normalizeAutoAnalyzeSeconds()}秒ごとに${currentJudgmentLevelLabel()}で再判定します。`);
  }
  void analyzeCurrentFrame();
});

autoAnalyzeButton.addEventListener("click", () => {
  if (!canAutoAnalyze()) return;
  if (autoAnalyzeTimer !== null) {
    stopAutoAnalyze();
    setProcessingState("待機中");
    setStatus("自動判定を停止しました。");
    return;
  }
  startAutoAnalyzeInterval();
  setStatus(`自動判定中です。${normalizeAutoAnalyzeSeconds()}秒ごとに${currentJudgmentLevelLabel()}で再判定します。`);
  void analyzeCurrentFrame({ silentIfBusy: true });
});

autoAnalyzeIntervalInput.addEventListener("change", () => {
  const seconds = normalizeAutoAnalyzeSeconds();
  if (autoAnalyzeTimer === null) return;
  startAutoAnalyzeInterval();
  setStatus(`自動判定中です。${seconds}秒ごとに${currentJudgmentLevelLabel()}で再判定します。`);
});

judgmentLevelSelect.addEventListener("change", () => {
  const label = currentJudgmentLevelLabel();
  if (autoAnalyzeTimer === null) {
    setStatus(`判定レベルを${label}に変更しました。次回の判定から反映されます。`);
    return;
  }
  setStatus(`自動判定中です。${normalizeAutoAnalyzeSeconds()}秒ごとに${label}で再判定します。`);
});

manualSignalButtons.forEach((button) => {
  button.addEventListener("click", () => setManualSignal(button.dataset.manualSignal));
});

fileInput.addEventListener("change", (event) => {
  const [file] = event.target.files;
  void loadFile(file);
});

videoScrubber.addEventListener("input", onVideoScrub);

uploadVideo.addEventListener("loadedmetadata", () => {
  videoScrubber.value = "0";
  syncAnalyzeControls();
  setProcessingState("判定待ち");
  setStatus("動画を読み込みました。再生位置のフレームで判定します。");
});

uploadVideo.addEventListener("timeupdate", () => {
  if (!uploadVideo.duration || Number.isNaN(uploadVideo.duration)) return;
  videoScrubber.value = String(uploadVideo.currentTime / uploadVideo.duration);
});

imagePreview.addEventListener("load", () => {
  syncAnalyzeControls();
  setProcessingState("判定待ち");
  setStatus("画像を読み込みました。AIで判定できます。");
});

window.addEventListener("beforeunload", () => {
  clearAutoAnalyzeCountdownTimer();
  stopCamera();
});

// ── 初期化 ────────────────────────────────────────────────

autoAnalyzeIntervalInput.value = String(AUTO_ANALYZE_DEFAULT_SECONDS);
window.setManualSignal = setManualSignal;

initTheme();
initDeviceName();
showEmptyState();
initChart();
void loadTodayHistory();
