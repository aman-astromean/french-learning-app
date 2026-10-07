# French Learning App

An app-ready French curriculum database spanning A0 to C2 topics. This repository contains 420 daily lessons across 60 weekly units, 2,000 conversation words with IPA and examples, quiz and flashcard data, pronunciation reference material, and learner-progress tables.

Open the [web prototype](web/README.md) for a working Apple-inspired interface with a daily dashboard, lessons, quizzes, flashcards, a course map, and local progress.

See [course documentation](french_course/README.md) for contents, build instructions, and practical limits. See [voice integration candidate](french_course/VOICE_INTEGRATION.md) for the pinned external repository and what is required before French speaking practice can use it.

## Rebuild

```bash
python3 french_course/build.py
python3 web/export_course.py
python3 -m http.server 8000
```

Then open `http://localhost:8000/web/` to explore the interface.

This regenerates `french_course/french_course.sqlite` and `french_course/course_days.csv` using only Python 3's standard library. The generated database is committed so a future web app can use it immediately.

The voice project at [BernieTv/ElevenLabs-Clone](https://github.com/BernieTv/ElevenLabs-Clone) remains an external integration candidate; its source code is not vendored here.
