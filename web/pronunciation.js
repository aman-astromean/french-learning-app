const locale = 'fr-FR';
const key = text => text.normalize('NFC').replace(/[’ʼ]/g, "'").trim().replace(/\s+/g, ' ');
let clips;
let indexRequest;
let active;
let ticket = 0;

// Preload just the index. Audio is downloaded only when the learner presses play.
export function loadPronunciation() {
  if (clips) return Promise.resolve(true);
  indexRequest ||= fetch('./audio/index.json').then(async response => {
    if (!response.ok) return false;
    const data = await response.json();
    if (data.voice !== 'ff_siwis' || !data.clips) return false;
    clips = data.clips;
    return true;
  }).catch(() => false).finally(() => { indexRequest = undefined; });
  return indexRequest;
}

function message(text) {
  document.querySelector('#speech-status').textContent = text;
}

export function stopPronunciation() {
  ticket++;
  const previous = active;
  active = undefined;
  if (previous?.audio) previous.audio.pause();
  if (previous?.utterance) window.speechSynthesis.cancel();
  previous?.button.setAttribute('aria-pressed', 'false');
  if (previous) message('');
}

export async function playPronunciation(button) {
  const repeat = active?.button === button;
  stopPronunciation();
  if (repeat) return;
  const text = key(button.dataset.speech || '');
  if (!text) return;
  const current = ticket;
  const slow = button.dataset.rate === 'slow';
  const finish = (status = '') => {
    if (current !== ticket) return;
    button.setAttribute('aria-pressed', 'false');
    active = undefined;
    message(status);
  };
  const start = (media, label) => {
    active = {button, ...media};
    button.setAttribute('aria-pressed', 'true');
    message(label + (slow ? ' · slow' : ''));
  };
  if (!clips) {
    message('Loading French audio…');
    const ready = await loadPronunciation();
    if (current !== ticket) return;
    if (!ready) {
      finish('French audio is temporarily unavailable. Tap Listen to retry.');
      return;
    }
  }
  const clip = Object.hasOwn(clips, text) ? clips[text] : '';
  if (typeof clip === 'string' && /^[a-f0-9]{24}\.mp3$/.test(clip)) {
    const audio = new Audio(`./audio/${clip}`);
    audio.playbackRate = slow ? 0.75 : 1;
    audio.preservesPitch = true;
    audio.onended = () => finish();
    start({audio}, 'French neural voice');
    try {
      await audio.play();
      if (current === ticket) audio.onerror = () => finish('Audio was interrupted. Tap Listen to retry.');
      return;
    } catch {
      if (current !== ticket) return;
      audio.pause();
      finish('Could not play the French recording. Tap Listen to retry.');
      return;
    }
  }
  const synth = window.speechSynthesis;
  const voices = synth?.getVoices().filter(v => /^fr(?:[-_]|$)/i.test(v.lang)) || [];
  const voice = voices.find(v => /^fr[-_]fr$/i.test(v.lang) && v.default)
    || voices.find(v => /^fr[-_]fr$/i.test(v.lang)) || voices.find(v => v.default) || voices[0];
  if (!voice || !window.SpeechSynthesisUtterance) {
    finish('No French device voice is available. Enable a French speech voice in your device settings or try another browser.');
    return;
  }
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.voice = voice;
  utterance.lang = voice.lang || locale;
  utterance.rate = slow ? 0.72 : 1;
  utterance.onend = () => finish();
  utterance.onerror = () => finish('The French device voice could not play. Try again or check your speech settings.');
  start({utterance}, `Device voice · ${voice.lang}`);
  try { synth.speak(utterance); }
  catch { finish('The French device voice could not play. Check your speech settings.'); }
}
