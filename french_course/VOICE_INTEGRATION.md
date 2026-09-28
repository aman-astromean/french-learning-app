# Voice integration candidate for the French learning app

Source: https://github.com/BernieTv/ElevenLabs-Clone.git  
Inspected commit: `5c3aff322c172ae714c57e930057065982f9f8a8` (2025-04-09).  
Local checkout: `../ElevenLabs-Clone` in the working workspace. The upstream GitHub repository is the durable source of the code; it is intentionally not bundled into this course archive. The database's `voice_integrations` table pins its identity and records that French support remains unverified.

## Actual reusable parts

- `StyleTTS2/api.py` exposes authenticated `POST /generate` with `{text, target_voice}` and returns a signed audio URL plus storage key; `GET /voices` and `/health` are present. A lesson example or flashcard can be submitted for synthesis. This path currently sets `phonemizer.backend.EspeakBackend(language='en-us')` in `StyleTTS2/libri_inference.py`; the configured models and voice references are LibriTTS-oriented. **Do not use the generated sound as a French pronunciation model without French model support and listening evaluation.** Changing just the language flag is insufficient.
- `seed-vc/api.py` exposes authenticated `POST /convert` with `{source_audio_key, target_voice}` and returns audio. It changes timbre, not speech recognition or pronunciation accuracy. The bundled target voices include impersonation references; use only voices with consent and suitable rights in a learning product.
- `Make-An-Audio/api.py` generates non-speech sound effects. It is optional for learning.
- The Next.js app has Inngest background jobs, S3 audio storage, history and playback, auth, and a voice picker. Reuse its service boundary and request/response shape if useful; there is no need to copy its whole user system into the course app.

## Practical integration path

1. Keep course content as the source of truth: `lessons.example_fr`, `grammar_topics.example_fr`, flashcard fronts, and eventually longer dialogues. Add a versioned audio asset for a particular text, locale (for example `fr-FR` or `fr-CA`), speaker and provider in `media_assets`.
2. Put a server-side adapter between the app and a French-tested TTS backend: request `{text, locale, voice_id, speaking_rate}`, return an audio asset key, duration, and status. Generate and cache lesson audio ahead of time; use the repo's authentication pattern and async queue if deploying its service. Never expose provider keys in the browser.
3. For learner speech, record audio with consent and use a **separate French ASR** to obtain a transcript. Compare content with valid alternatives, then add calibrated phoneme/prosody feedback using a pronunciation assessment component. This repo's voice conversion is not ASR and does not grade pronunciation.
4. Test French accents, liaison, nasal vowels, sentence prosody, and fr-FR/fr-CA variants with speakers. Check latency, GPU cost, storage retention, abuse controls, accessibility, and audio licensing before production use.
5. Review each component's terms before distribution: the repo root and StyleTTS2 code are MIT, while bundled `seed-vc` has GPL-3.0; model weights and training data can have separate rights. Avoid treating the root license as covering every nested component.

## Current state

The repo is cloned and inspected; no models or audio service were launched. Its Docker Compose file refers to image `bekzod47` for all three services and asks for NVIDIA GPU reservations; model downloads and S3 credentials are not supplied by the course package. French TTS, speech recognition, and pronunciation scoring have **not** been verified. `voice_integrations.integration_status='candidate'` and `french_verified=0` encode that state.
