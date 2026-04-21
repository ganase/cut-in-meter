const startCameraButton = document.querySelector("#startCameraButton");
const stopCameraButton = document.querySelector("#stopCameraButton");
const captureButton = document.querySelector("#captureButton");
const analyzeButton = document.querySelector("#analyzeButton");
const autoAnalyzeButton = document.querySelector("#autoAnalyzeButton");
const manualSignalButtons = document.querySelectorAll("[data-manual-signal]");
const autoAnalyzeIntervalInput = document.querySelector("#autoAnalyzeIntervalInput");
const fileInput = document.querySelector("#fileInput");
const cameraPreview = document.querySelector("#cameraPreview");
const uploadVideo = document.querySelector("#uploadVideo");
const imagePreview = document.querySelector("#imagePreview");
const emptyPreview = document.querySelector("#emptyPreview");
const sourceLabel = document.querySelector("#sourceLabel");
const videoScrubberWrap = document.querySelector("#videoScrubberWrap");
const videoScrubber = document.querySelector("#videoScrubber");
const trafficLight = document.querySelector("#trafficLight");
const scoreValue = document.querySelector("#scoreValue");
const confidenceValue = document.querySelector("#confidenceValue");
const resultAgeValue = document.querySelector("#resultAgeValue");
const headline = document.querySelector("#headline");
const reasons = document.querySelector("#reasons");
const playfulSuggestion = document.querySelector("#playfulSuggestion");
const caution = document.querySelector("#caution");
const statusMessage = document.querySelector("#statusMessage");
const workingCanvas = document.querySelector("#workingCanvas");

let cameraStream = null;
let currentSource = null;
let autoAnalyzeTimer = null;
let resultAgeTimer = null;
let analyzeInFlight = false;
let lastGeneratedAtMs = null;

const AUTO_ANALYZE_DEFAULT_SECONDS = 30;
const AUTO_ANALYZE_MIN_SECONDS = 2;
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

function releaseCurrentObjectUrl() {
  if (currentSource?.objectUrl) {
    URL.revokeObjectURL(currentSource.objectUrl);
  }
}

function setStatus(message) {
  statusMessage.textContent = message;
}

function setSource(name) {
  sourceLabel.textContent = name;
}

function hideAllMedia() {
  cameraPreview.classList.add("hidden");
  uploadVideo.classList.add("hidden");
  imagePreview.classList.add("hidden");
  emptyPreview.classList.add("hidden");
}

function canAutoAnalyze() {
  return currentSource?.kind === "camera";
}

function syncAnalyzeControls() {
  analyzeButton.disabled = !currentSource;
  autoAnalyzeButton.disabled = !canAutoAnalyze();
  autoAnalyzeButton.textContent = autoAnalyzeTimer === null ? "自動判定を開始" : "自動判定を停止";
}

function clearResultAgeTimer() {
  if (resultAgeTimer !== null) {
    window.clearInterval(resultAgeTimer);
    resultAgeTimer = null;
  }
}

function formatElapsedSeconds(timestampMs) {
  const elapsedMs = Math.max(0, Date.now() - timestampMs);
  const seconds = Math.floor(elapsedMs / 1000);
  return `${seconds}秒前`;
}

function renderResultAge() {
  if (lastGeneratedAtMs === null || Number.isNaN(lastGeneratedAtMs)) {
    resultAgeValue.textContent = "--";
    return;
  }
  resultAgeValue.textContent = formatElapsedSeconds(lastGeneratedAtMs);
}

function currentResultAgeLabel() {
  return lastGeneratedAtMs === null ? "たった今" : formatElapsedSeconds(lastGeneratedAtMs);
}

function setResultTimestamp(timestamp) {
  lastGeneratedAtMs = typeof timestamp === "number" && Number.isFinite(timestamp) ? timestamp : null;
  clearResultAgeTimer();
  renderResultAge();
  if (lastGeneratedAtMs !== null) {
    resultAgeTimer = window.setInterval(renderResultAge, 1000);
  }
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
  if (!content) {
    return;
  }

  stopAutoAnalyze();
  trafficLight.dataset.signal = signal;
  scoreValue.textContent = "--";
  confidenceValue.textContent = "--";
  headline.textContent = content.headline;
  setReasons(content.reasons);
  playfulSuggestion.textContent = content.playfulSuggestion;
  caution.textContent = "手動で信号を変更しています。AI判定を行うと結果は上書きされます。";
  setResultTimestamp(null);
  setStatus(`手動で${content.label}信号に切り替えました。`);
}

function showEmptyState() {
  stopAutoAnalyze();
  releaseCurrentObjectUrl();
  hideAllMedia();
  emptyPreview.classList.remove("hidden");
  videoScrubberWrap.classList.add("hidden");
  currentSource = null;
  captureButton.disabled = true;
  stopCameraButton.disabled = true;
  setSource("ソース未選択");
  setResultTimestamp(null);
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
  syncAnalyzeControls();
}

function startAutoAnalyzeInterval() {
  if (!canAutoAnalyze()) {
    stopAutoAnalyze();
    return;
  }

  stopAutoAnalyze();
  const seconds = normalizeAutoAnalyzeSeconds();
  autoAnalyzeTimer = window.setInterval(() => {
    void analyzeCurrentFrame({ silentIfBusy: true });
  }, seconds * 1000);
  syncAnalyzeControls();
}

function stopCamera() {
  if (cameraStream) {
    for (const track of cameraStream.getTracks()) {
      track.stop();
    }
    cameraStream = null;
  }
  cameraPreview.srcObject = null;
  stopAutoAnalyze();
  if (!currentSource || currentSource.kind === "camera") {
    showEmptyState();
  } else {
    stopCameraButton.disabled = true;
    captureButton.disabled = true;
  }
}

async function startCamera() {
  try {
    stopCamera();
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: "user" },
      audio: false,
    });

    cameraStream = stream;
    hideAllMedia();
    cameraPreview.classList.remove("hidden");
    cameraPreview.srcObject = stream;
    currentSource = { kind: "camera" };
    setSource("ライブカメラ");
    stopCameraButton.disabled = false;
    captureButton.disabled = false;
    syncAnalyzeControls();
    setStatus("カメラの準備ができました。AIで判定を押すと自動更新が始まります。");
  } catch (error) {
    console.error(error);
    setStatus("カメラを開始できませんでした。権限設定を確認してください。");
  }
}

function drawMediaToCanvas(element) {
  const context = workingCanvas.getContext("2d");
  const sourceWidth = element.videoWidth || element.naturalWidth || element.width;
  const sourceHeight = element.videoHeight || element.naturalHeight || element.height;
  const maxSide = 1280;
  const scale = Math.min(1, maxSide / Math.max(sourceWidth, sourceHeight));
  workingCanvas.width = Math.max(1, Math.round(sourceWidth * scale));
  workingCanvas.height = Math.max(1, Math.round(sourceHeight * scale));
  context.drawImage(element, 0, 0, workingCanvas.width, workingCanvas.height);
  return workingCanvas.toDataURL("image/jpeg", 0.86);
}

async function captureCurrentFrame() {
  if (!currentSource) {
    return null;
  }
  if (currentSource.kind === "camera") {
    return drawMediaToCanvas(cameraPreview);
  }
  if (currentSource.kind === "upload-image") {
    return drawMediaToCanvas(imagePreview);
  }
  if (currentSource.kind === "upload-video") {
    return drawMediaToCanvas(uploadVideo);
  }
  return null;
}

function updateResult(result) {
  trafficLight.dataset.signal = result.signal;
  scoreValue.textContent = String(result.score);
  confidenceValue.textContent = `${result.confidence}%`;
  headline.textContent = result.headline;
  setReasons(result.reasons);
  playfulSuggestion.textContent = result.playfulSuggestion;
  caution.textContent = result.caution;
  setResultTimestamp(Date.parse(result.generatedAt));
}

async function analyzeCurrentFrame(options = {}) {
  const { silentIfBusy = false } = options;

  if (analyzeInFlight) {
    if (!silentIfBusy) {
      setStatus("現在の判定が終わるまでお待ちください。");
    }
    return;
  }

  const imageDataUrl = await captureCurrentFrame();
  if (!imageDataUrl) {
    setStatus("先にカメラまたはファイルを選択してください。");
    return;
  }

  analyzeInFlight = true;
  analyzeButton.disabled = true;
  setStatus("AIが判定中です...");

  try {
    const response = await fetch("/api/score", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        imageDataUrl,
        sourceLabel: sourceLabel.textContent,
      }),
    });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.error || "Unknown API error");
    }
    updateResult(payload);
    setStatus(`${payload.model} が判定しました。最終判定は ${currentResultAgeLabel()} です。`);
  } catch (error) {
    console.error(error);
    setStatus(`判定に失敗しました: ${error.message}`);
  } finally {
    analyzeInFlight = false;
    syncAnalyzeControls();
  }
}

function onVideoScrub() {
  if (!uploadVideo.duration || Number.isNaN(uploadVideo.duration)) {
    return;
  }
  uploadVideo.currentTime = Number(videoScrubber.value) * uploadVideo.duration;
}

async function loadFile(file) {
  stopAutoAnalyze();
  releaseCurrentObjectUrl();

  if (!file) {
    showEmptyState();
    return;
  }

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
    setStatus("動画を読み込み中です...");
    return;
  }

  currentSource = null;
  syncAnalyzeControls();
  setStatus("未対応のファイル形式です。画像か動画を選択してください。");
}

startCameraButton.addEventListener("click", startCamera);
stopCameraButton.addEventListener("click", stopCamera);
captureButton.addEventListener("click", async () => {
  if (!cameraStream) {
    return;
  }
  stopAutoAnalyze();
  const snapshot = await captureCurrentFrame();
  hideAllMedia();
  imagePreview.src = snapshot;
  imagePreview.classList.remove("hidden");
  currentSource = { kind: "upload-image", dataUrl: snapshot };
  captureButton.disabled = true;
  stopCameraButton.disabled = false;
  setSource("カメラ静止画");
  syncAnalyzeControls();
  setStatus("カメラ映像を静止画として固定しました。");
});

analyzeButton.addEventListener("click", () => {
  if (canAutoAnalyze()) {
    startAutoAnalyzeInterval();
    setStatus(`自動判定中です。${normalizeAutoAnalyzeSeconds()}秒ごとに再判定します。`);
  }
  void analyzeCurrentFrame();
});

autoAnalyzeButton.addEventListener("click", () => {
  if (!canAutoAnalyze()) {
    return;
  }

  if (autoAnalyzeTimer !== null) {
    stopAutoAnalyze();
    setStatus("自動判定を停止しました。");
    return;
  }

  startAutoAnalyzeInterval();
  setStatus(`自動判定中です。${normalizeAutoAnalyzeSeconds()}秒ごとに再判定します。`);
  void analyzeCurrentFrame({ silentIfBusy: true });
});

autoAnalyzeIntervalInput.addEventListener("change", () => {
  const seconds = normalizeAutoAnalyzeSeconds();
  if (autoAnalyzeTimer === null) {
    return;
  }

  startAutoAnalyzeInterval();
  setStatus(`自動判定中です。${seconds}秒ごとに再判定します。`);
});

manualSignalButtons.forEach((button) => {
  button.addEventListener("click", () => {
    setManualSignal(button.dataset.manualSignal);
  });
});

fileInput.addEventListener("change", (event) => {
  const [file] = event.target.files;
  void loadFile(file);
});

videoScrubber.addEventListener("input", onVideoScrub);

uploadVideo.addEventListener("loadedmetadata", () => {
  videoScrubber.value = "0";
  syncAnalyzeControls();
  setStatus("動画を読み込みました。再生位置のフレームで判定します。");
});

uploadVideo.addEventListener("timeupdate", () => {
  if (!uploadVideo.duration || Number.isNaN(uploadVideo.duration)) {
    return;
  }
  videoScrubber.value = String(uploadVideo.currentTime / uploadVideo.duration);
});

imagePreview.addEventListener("load", () => {
  syncAnalyzeControls();
  setStatus("画像を読み込みました。AIで判定できます。");
});

window.addEventListener("beforeunload", () => {
  clearResultAgeTimer();
  stopCamera();
});

autoAnalyzeIntervalInput.value = String(AUTO_ANALYZE_DEFAULT_SECONDS);
window.setManualSignal = setManualSignal;
showEmptyState();
