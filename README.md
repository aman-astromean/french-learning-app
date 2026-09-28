# French Learning App

An app-ready French curriculum database spanning A0 to C2 topics. This repository contains 420 daily lessons across 60 weekly units, quiz and flashcard data, pronunciation reference material, and learner-progress tables.

See [course documentation](french_course/README.md) for contents, build instructions, and practical limits. See [voice integration candidate](french_course/VOICE_INTEGRATION.md) for the pinned external repository and what is required before French speaking practice can use it.

## Rebuild

```bash
python3 french_course/build.py
```

This regenerates `french_course/french_course.sqlite` and `french_course/course_days.csv` using only Python 3's standard library. The generated database is committed so a future web app can use it immediately.

The voice project at [BernieTv/ElevenLabs-Clone](https://github.com/BernieTv/ElevenLabs-Clone) remains an external integration candidate; its source code is not vendored here.
