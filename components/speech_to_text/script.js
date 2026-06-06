const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recog = new SpeechRecognition();
let translator = null;
let finalizedTranslationHistory = "";
let recording = false;
let translation;

function dispatchRecordingState(active) {
  document.dispatchEvent(new CustomEvent('hackstreet:recording', { detail: { active } }));
}

async function handleButtonClick() {
  const recButton = document.getElementById("rec-button");
  if (recording) {
    recog.stop();
    recButton.innerText = "⬡ Record";
    recording = false;
    dispatchRecordingState(false);
    return;
  }
  if (!translator) {
    recButton.innerText = "Downloading model...";
    recButton.disabled = true;
    try {
      translator = await Translator.create({
        sourceLanguage: "ja",
        targetLanguage: "en",
      });
      console.log("Translator initialized successfully!");
    } catch (error) {
      console.error("Failed to initialize translator:", error);
      recButton.innerText = "⬡ Record";
      recButton.disabled = false;
      return;
    }
  }
  recButton.disabled = false;
  recButton.innerText = "◼ Stop";
  recording = true;
  dispatchRecordingState(true);
  recog.start();
  recog.onstart = () => console.log("Recognition started");
  recog.onaudiostart = () => console.log("Audio started");
  recog.onspeechstart = () => console.log("Speech detected");
  recog.onerror = (event) => console.error("Speech recognition error:", event.error);
  recog.onend = () => {
    console.log("Recognition ended");
    console.log(translation);
    recButton.innerText = "⬡ Record";
    recording = false;
    dispatchRecordingState(false);
  };
  recog.onresult = parseRecognition;
}

async function parseRecognition(event) {
  const results = Array.from(event.results);
  const transcript = results
    .map((result) => result[0])
    .map((result) => result.transcript)
    .join("");
  document.getElementById("text").innerHTML = transcript;
  try {
    translation = await translator.translate(transcript);
  } catch (error) {
    console.error("Translation error:", error);
  }
}

recog.lang = "ja";
recog.interimResults = true;
recog.continuous = true;

const recButton = document.getElementById("rec-button");
recButton.addEventListener("click", handleButtonClick);
