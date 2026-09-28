# Parole web prototype

A responsive, dependency-free front end for the French course database. It includes the daily dashboard, a 60-unit course browser, usable lessons and checkpoint quizzes, flashcards, and device-local progress. It has no account server or recorded voice yet.

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
