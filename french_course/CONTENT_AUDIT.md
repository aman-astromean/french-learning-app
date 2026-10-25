# Completion audit

This update completes the unfinished reference data for the existing 3,000-word
bank. It does not claim to contain every French word or a professionally
validated fluency course.

| Area | Before | After |
|---|---:|---:|
| Distinct vocabulary entries | 3,000 | 3,000 |
| Pending verb entries | 65 | 0 |
| Unclassified words | 445 | 0 |
| Base verbs in reference | 371 | 439 |
| Canonical conjugation cells | 7,932 | 35,488 |
| Pronominal constructions | 0 | 14 |
| Pronominal conjugation cells | 0 | 798 |
| Citation-question/draft examples | 1,000 | 0 |
| Noun/adjective inflection rows | 0 | 5,479 |
| Sentence-building patterns | 0 | 80 |
| Sentence-building tasks | 0 | 160 |
| Standalone phoneme guides | 0 | 37 |
| Connected-speech rules | 0 | 13 |

## Coverage rules

- A normal finite paradigm expects six persons; affirmative imperatives expect
  tu/nous/vous. Impersonal *falloir* expects only il and has no imperative.
- All stored paradigms have their applicable persons. Conditional present uses
  the consistent pair `mood=conditional`, `tense=present`.
- Compound models document auxiliary and agreement choices. Canonical forms
  do not incorporate an automatically inferred speaker gender. Variants and
  construction notes supply the relevant alternatives.
- Every vocabulary word has IPA and sound-guide links. Finite cells have
  dictionary IPA where supplied (19,453); 261 missing citation transcriptions
  are flagged. Compound cells (15,774) provide auxiliary/participle IPA parts,
  not invented recordings or connected-phrase transcriptions.
- All examples are contextual: 212 are authored and 2,788 come from a corpus.
  All remain editorially unreviewed. Automated sense matching can still be
  wrong; use educator review before treating the bank as production teaching
  content. Classification and noun gender also depend on sense and referent.
- Word-to-pattern links are grammar references. They do not assert that an
  arbitrary headword can replace a model noun or verb without other changes.

## Verification

`build.py` checks counts, foreign keys, integrity, required fields and applicable
present-tense persons. `test_completion.py` adds ten regression checks covering
impersonal verbs, irregular spellings, normalized tenses, auxiliary choice,
agreement variants, lexical inflections, reflexive routines, homograph IPA and
sentence component reconstruction. JavaScript syntax and JSON exports are
checked separately.

The course-database GitHub workflow rebuilds and tests the large SQLite artifact from checked-in sources, then commits it to main. Its path filters exclude artifact-only commits to avoid a rebuild loop.
