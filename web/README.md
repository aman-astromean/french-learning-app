# Parole web prototype

A responsive, dependency-free front end for the French course database. It includes the daily dashboard, a 60-unit course browser, lessons and checkpoint quizzes, flashcards, and device-local progress. The first two weeks now present worked teaching steps and a pronunciation panel with IPA, articulation cues and sound contrasts. Later lessons show guided steps and level-appropriate vocabulary. It has no account server.

## Run locally

From the repository root:

```bash
python3 french_course/build.py
python3 web/export_course.py
python3 -m http.server 8000
```

Open `http://localhost:8000/web/`. Serve via HTTP; opening `index.html` directly from a file URL will block JSON requests in most browsers.

## GitHub Pages

The workflow in `.github/workflows/pages.yml` deploys the `web/` directory on changes to the web app or on manual dispatch. After GitHub Pages is enabled with **GitHub Actions** as its source, the expected project URL is `https://aman-astromean.github.io/french-learning-app/`. The URL is usable only after a successful deployment. On GitHub Free, this requires the repository to be public; that exposes the repository's curriculum, SQLite database, and source code as well as the web app. The published site itself uses static JSON and keeps learner progress only in each browser.

The SQLite database remains the canonical content source. `web/export_course.py` creates small static JSON files split by CEFR level for the prototype. The UI never connects directly to the database. A future backend can replace these static fetches while keeping the same lesson and exercise IDs.

Progress is stored under `parole-progress-v1` in localStorage. Quiz answer flags exist in the static data and are suitable only for a prototype; move grading to a server before building competitive or certified assessments. Speaking and writing answers show a model for self-check and are not automatically marked correct. The voice integration candidate is documented in `../french_course/VOICE_INTEGRATION.md`.

Design follows the principles in Apple's Human Interface Guidelines: legible type, content hierarchy, adaptive navigation, accessible controls, light/dark appearance, and restrained translucent navigation. This is an independent web design inspired by those principles, not an Apple product or a pixel copy.

## Expanded learning reference

Lesson vocabulary now exposes IPA, contextual examples and present-tense forms in expandable cards. Lessons with sentence patterns show labelled components and a model-rebuilding task. Full exports are in `data/verb_reference.json`, `data/lexical_reference.json` and `data/sentence_reference.json`; the original `conversation_words.json` contract retains its canonical conjugation list. Examples remain unreviewed, and the interface does not claim recorded audio or automatic pronunciation scoring.

## Weekly skills extensions

From A1 onward, days 2, 3, 5, 6 and 7 of each unit offer optional reading, dialogue preparation, writing, speaking and retrieval. The expanded panel displays its extra suggested time. Comprehension radio groups are self-check practice: reveal the answer and supporting passage after choosing. They do not alter the checkpoint score. Open production tasks include rubrics and are done outside the app; responses are not stored. Dialogue scripts can be played with a French device voice. Full data is available in `data/enrichment_reference.json`, with scheduled subsets in the per-level exports. See `../french_course/ENRICHMENT_AUDIT.md` for review scope, schema and limitations.

## French pronunciation playback

Use **Listen** or **Slow** on sound examples, words and flashcards. Lesson examples and dialogue turns also support playback. Press the active button again to stop. Playback is initiated by the learner, and IPA remains visible alongside the sound drills.

The Pages workflow generates a starter set of `fr-FR` MP3 clips with the [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M) model and its `ff_siwis` voice. It pins the model revision and builds audio from the course’s first two weeks and common vocabulary. Static clips need no API key or microphone and are downloaded on demand. The remaining content uses an available French voice through the [Web Speech API](https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesis/getVoices). Device voices and accents vary; the app will report a missing French voice rather than select an English one. A French system voice may need to be enabled in device settings.

The clips are synthetic learning aids; they have not been independently reviewed by French instructors. Playback does not record or score the learner. Local builds work with device voices unless the optional `web/generate_pronunciation.py` step is run with the dependencies listed in the Pages workflow.

## Verb Conjugation and Dictionary

Both sections are in the desktop sidebar and the mobile navigation. Search by French spelling, English meaning, or a stored form. Accents are optional when searching. Press Enter to open the first result, or pick another match from the list.

- **Verb Conjugation:** 439 base verbs and 14 pronominal entries, with all forms available in the course database. Open a tense to see its subjects, forms, available IPA, audio and variants. Entries include contextual examples and auxiliary or usage notes.
- **Dictionary:** 3,000 course words with English meanings, IPA, audio and bilingual examples. Nouns and adjectives show available inflections. Entries link to applicable sentence patterns and to the conjugation table when a verb reference is available.

`web/export_course.py` generates the search indexes and entry files under `data/reference/`. Opening a reference tab loads its search index; selecting an entry loads only that group of records. Audio uses the same neural clips and French device voice fallback as lessons.
