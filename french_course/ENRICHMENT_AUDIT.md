# Reference-informed weekly skills expansion

## Content scope

The expansion addresses gaps in grammar practice, everyday reading, writing, speaking, and advanced text organisation. The readings, scripts, and exercises were written for this project. All scenarios and sample source notes are fictional. The practice packs do not reproduce official exam papers, timing rules, or marking schemes.

## Added content

| Target level | Existing units | Weekly packs | Readings | Six-turn dialogues | Comprehension questions | Writing tasks | Speaking tasks |
|---|---|---:|---:|---:|---:|---:|---:|
| A1 | 3–12 | 10 | 10 | 10 | 50 | 10 | 10 |
| A2 | 13–22 | 10 | 10 | 10 | 50 | 10 | 10 |
| B1 | 23–34 | 12 | 12 | 12 | 60 | 12 | 12 |
| B2 | 35–44 | 10 | 10 | 10 | 50 | 10 | 10 |
| C1 | 45–52 | 8 | 8 | 8 | 40 | 8 | 8 |
| C2 | 53–60 | 8 | 8 | 8 | 40 | 8 | 8 |
| **Total** | **3–60** | **58** | **58** | **58** | **290** | **58** | **58** |

The readings contain 6,782 whitespace-delimited French words in this version. There are also 348 dialogue turns, 174 contextual expression entries, 348 bidirectional flashcards, 464 task-specific rubric rows, 58 grammar focus notes and 290 scheduled extension activities. Expression entries are contextual learning items, not 174 distinct new vocabulary lemmas. No additions are made to the existing 3,000-word bank or verb inventory by this expansion.

Every reading has three comprehension questions. Every dialogue has two. Each question has three options, one correct option, an evidence excerpt and a short answer explanation. These questions are stored separately from the existing checkpoint exercises. They are self-check activities in the static web interface and do not change the checkpoint completion score.

## Weekly progression

The original 420-day sequence and required lesson estimates remain intact. A0 days 1–14 retain the pronunciation-first sequence. Each A1–C2 unit gains optional extensions:

| Day within week | Activity | Extra suggested minutes |
|---|---|---:|
| 2 | Reading, comprehension and contextual expressions | 12 |
| 3 | Dialogue, comprehension and pronunciation rehearsal | 10 |
| 5 | Writing and revision | 15 |
| 6 | Speaking and interaction | 12 |
| 7 | Retrieval, revision and transfer | 10 |

A1 uses short personal and practical texts. A2 adds past events, comparisons and transactions. B1 develops narrative, reasons, workplace learning and clear correspondence. B2 adds qualified arguments, causal caution, mediation and professional writing. C1 focuses on register, implication, cohesion, evidence and extended explanation. C2 targets modal nuance, idioms, rhetorical fairness, dense-source synthesis and audience adaptation. Level labels indicate intended curriculum difficulty; they have not been independently calibrated.

## Accuracy decisions

The reference collection contains errors and oversimplifications. Newly authored notes explicitly distinguish person/number from gender in reflexive pronouns, following direct objects in pronominal agreement, imperfect background from completed events, restriction from negation, and source attribution from certainty. For example, **elle ne s’est pas lavé les cheveux** has negation around the finite auxiliary, and no subject agreement on *lavé* because the direct object follows. The supplementary notes also distinguish subjunctive triggers from the conjunction *que* itself, expletive *ne* from negation, and *après que* + indicative from *avant que* + subjunctive.

At advanced levels, a hypothesis is not presented as proof, a provisional agreement as a confirmed commitment, or a small fictional consultation as representative evidence. Open production tasks remain ungraded, with rubrics for task fulfilment, organisation, language and communication.

## Schema and consumption

`skill_packs` links one pack to each existing A1–C2 unit. `skill_resources` stores readings and dialogue scripts; `dialogue_turns` preserves speaker order. `comprehension_questions` and `comprehension_options` hold questions, evidence and answer keys. `production_tasks` and `production_rubrics` support open tasks. `skill_expressions` supplies contextual phrases; their cards also enter the existing `flashcards` table. `skill_schedule` links activities to existing lessons with explicit extra minutes. `skill_pronunciation` links to existing sound rules, IPA examples and rehearsal guidance.

`web/export_course.py` exports the full reference as `enrichment_reference.json` and embeds the scheduled activity into the relevant day’s level JSON. The lesson view offers expandable optional practice. Native radio groups allow a choice before revealing the evidence; writing/speaking work is done in a notebook or with a partner, not collected or saved by this extension.

## Validation and remaining work

Automated checks cover complete unit coverage, counts, foreign keys, evidence inclusion, unique answer options, mixed correct-option positions, text-length floors, schedule placement, honest media/assessment status and export consistency. They do not establish grammatical perfection or independent CEFR calibration. Every new pack is marked `editorial_review_pending` for educator review.

Dialogue scripts have **no recordings**. Existing sound guidance is reused; full-sentence IPA is not fabricated. Genuine listening assessment, validated French synthesis, speech recognition, teacher feedback, longitudinal learner validation and larger advanced source dossiers remain future work. Finishing these activities alone does not certify fluency or C2 proficiency.
