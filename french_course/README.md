# French Learning Course Database

A runnable, English-supported French curriculum seed for a future learning app. Start at day 1 and move through 60 seven-day units (420 days). The first two weeks are explicitly sequenced from alphabet and phonetics through numbers to first sentence patterns. Later units introduce grammar and communication across A1–C2. The levels are planning labels aligned broadly with the Council of Europe's CEFR, **not a certification or a promise of fluency in 420 calendar days**. Learners should repeat units as needed.

## Quick start

Requires Python 3 and SQLite with JSON support. Run `python3 build.py` in this folder to regenerate `french_course.sqlite` and `course_days.csv`. Or open the supplied SQLite database directly. There are no external packages.

```sql
PRAGMA foreign_keys=ON;
SELECT * FROM daily_course WHERE day_number BETWEEN 1 AND 14;
SELECT e.id,e.kind,e.prompt,c.choice_text,c.correct
FROM exercises e LEFT JOIN exercise_choices c ON c.exercise_id=e.id
WHERE e.lesson_id=7 ORDER BY e.position,c.position;
SELECT * FROM flashcards WHERE lesson_id=1;
SELECT verb_id,person,form FROM conjugations WHERE verb_id=1 AND mood='indicative' AND tense='present';
```

## Coverage

| Stage | Weeks | Days | Main outcomes |
|---|---:|---:|---|
| A0 | 2 | 1–14 | Alphabet names and word sounds, oral and nasal vowels, accents, silent letters, numbers 0–100, pronouns and first sentences |
| A1 | 10 | 15–84 | Basic questions, present tense, nouns, articles, adjectives, negation, daily transactions |
| A2 | 10 | 85–154 | Routine interaction, passé composé, imparfait, future, objects, travel |
| B1 | 12 | 155–238 | Narratives, opinions, conditionals, subjunctive, correspondence |
| B2 | 10 | 239–308 | Argument, complex clauses, pluperfect, hypothesis, mediation |
| C1 | 8 | 309–364 | Register, implication, cohesive writing, negotiation, extended speaking |
| C2 | 8 | 365–420 | Nuance, rhetorical control, source synthesis, literary interpretation |

The package contains **420 daily lesson rows**, **60 weekly review days**, **1,858 exercises**, **1,474 flashcards**, **333 curated lexemes**, **101 numbers**, **26 alphabet letters**, **70 lesson-linked pronunciation items**, **17 sound patterns**, **82 verbs with 1,896 stored conjugated forms**, and **67 supplementary reference notes**. The 14 A0 days have four worked teaching steps each, skill-specific checks, pronunciation breakdowns where relevant, and a self-check task. Later days have guided recall, noticing, transfer and production tasks; weekly reviews from A1–C2 add level-specific performance prompts and self-check criteria. They still need richer dialogues, texts and educator review. Each lesson is linked to a unit and prerequisite; learner and review tables start empty.

## Data model and daily app flow

`levels → units → lessons → lesson_blocks` provides course navigation and teaching content. `pronunciation_items` stores grapheme, IPA, example IPA, articulation cue and contrast for early lessons. `grammar_topics`, `reference_notes`, `lexemes`, `alphabet`, `numbers`, `sound_patterns`, `verbs`, and `conjugations` hold reusable reference content. `exercises`, `exercise_choices`, and `flashcards` provide activities. `learners`, `lesson_progress`, `attempts`, and `flashcard_reviews` support individual state. `media_assets` provides a future audio/transcript link but contains no fake recordings. All IDs are deterministic on rebuild.

1. Show the next lesson from `lessons` by `day_number`, optionally unlock it only when its row in `lesson_prerequisites` is complete.
2. Present `lesson_blocks` in position order, the modeled example, and the lesson's flashcards.
3. Score `choice` questions by `exercise_choices.correct`; shuffle choices in the UI while preserving choice IDs. The seeded choice positions are rotated, but do not expose answer flags or the answer field to the client before submission.
4. Treat `production` as self-check or manually/AI reviewed. Exact string matching is invalid because other translations can be correct. Save the response in `attempts` with `is_correct=NULL` until reviewed.
5. On review day, require at least 80% on its six objective questions (five correct); use the open response as additional practice. Retake missed concepts. **Do not automatically award an official CEFR level**.
6. Create `flashcard_reviews` for a learner as cards are introduced; query `due_at` for retrieval practice. `stability`, `difficulty`, and `interval_days` are reserved for a spaced-repetition algorithm chosen by the app. This seed intentionally does not claim a validated scheduler.

Suggested assessment rubric for speaking/writing: communicative success, range, grammatical control, pronunciation or organization, and audience/register. Score each 0–4; keep both assessor feedback and original response. Listening requires recorded audio; pronunciation requires audio models and human-calibrated speech evaluation.

## Voice integration candidate

The project records [BernieTv/ElevenLabs-Clone](VOICE_INTEGRATION.md) at a pinned commit in `voice_integrations` as a candidate for future speech generation and voice features. The repo is kept as a separate checkout. Its current TTS path is configured for English, and it does not provide French speech assessment. See `VOICE_INTEGRATION.md` for the integration boundary and requirements.

## Content boundaries and next editorial work

This is an executable **course foundation across all stages**, with deeply authored A0 lessons and a structured, still concise later path. It is not yet a complete set of graded readings, recorded dialogues, authentic listening, professionally voiced phonetics, thousands of headwords, or fully validated high-level assessment tasks. For expert communication, add sustained texts, varied real-world registers and regional accents, discussion partners, feedback, and externally assessed performance. `C2` is advanced communicative competence, not a fixed vocabulary count or native-speaker identity.

A content editor should verify each example and translation with a qualified French educator, write varied distractors and explanations, attach licensed/recorded audio, expand verb paradigms and lexicon, author longer reading/listening tasks, and pilot the checkpoints with learners. Some English prompts allow several valid French answers; open responses deliberately remain ungraded.

## Provenance and design

The examples and course sequence in this package were authored for this project. User-provided A1–B1 worksheets in Drive informed the topic ordering; their private links and content are not embedded in this public repository. The worksheets include some errors, so they are references for planning, not an authority for answers. The CEFR is used as a broad scope framework; the Council of Europe's [CEFR descriptors](https://www.coe.int/en/web/common-european-framework-reference-languages/cefr-descriptors) and [Companion volume overview](https://www.coe.int/en/web/common-european-framework-reference-languages) describe proficiency scales, including mediation and online interaction. Its [phonological competence guidance](https://www.coe.int/en/web/common-european-framework-reference-languages/phonological-competence) separates sound articulation and prosody. IPA here is a broad metropolitan model and varies by region. No CEFR descriptors or third-party lessons are copied into the database.
