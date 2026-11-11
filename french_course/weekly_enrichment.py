"""Load original skills content informed by a selective review of private references.

No reference passages, private file identifiers or recordings are imported.
These level labels are curriculum targets, not independently certified CEFR ratings.
"""
import json
from enrichment.a1 import PACKS as A1
from enrichment.a2 import PACKS as A2
from enrichment.b1 import PACKS as B1
from enrichment.b2 import PACKS as B2
from enrichment.advanced import PACKS as ADVANCED

PACKS = A1 + A2 + B1 + B2 + ADVANCED

def apply(db):
    assert sorted(p['unit'] for p in PACKS) == list(range(3,61))
    for p in PACKS:
        unit = p['unit']
        level = db.execute('SELECT level_code FROM units WHERE id=?',(unit,)).fetchone()[0]
        days = dict(db.execute('SELECT day_in_unit,id FROM lessons WHERE unit_id=?',(unit,)))
        db.execute('INSERT INTO skill_packs VALUES (?,?,?,?,?,?)',(unit,p['title'],p['summary'],p['grammar'],'original_authored','editorial_review_pending'))
        for kind, text, questions in [('reading',p['text'],p['questions']),('dialogue','\n'.join(f'{s}: {t}' for s,t in p['dialogue']),p['dialogue_questions'])]:
            rid=db.execute('INSERT INTO skill_resources(unit_id,kind,title,text_fr,summary_en,audio_status) VALUES (?,?,?,?,?,?)',(unit,kind,p['title'],text,p['summary'],'not_recorded')).lastrowid
            if kind=='dialogue':
                db.executemany('INSERT INTO dialogue_turns VALUES (?,?,?,?)',[(rid,i,s,t) for i,(s,t) in enumerate(p['dialogue'],1)])
            for i,(question,correct,wrong1,wrong2,evidence) in enumerate(questions,1):
                assert evidence.casefold() in text.casefold(), (unit,kind,evidence)
                assert len({correct,wrong1,wrong2}) == 3
                qid=db.execute('INSERT INTO comprehension_questions(resource_id,position,prompt_fr,evidence_fr,explanation_en) VALUES (?,?,?,?,?)',(rid,i,question,evidence,'The answer follows from this passage: « '+evidence+' ». Return to the surrounding sentence to check who, when and under what conditions.')).lastrowid
                options=[(correct,1),(wrong1,0),(wrong2,0)]
                shift=(unit+i+(kind=='dialogue'))%3
                options=options[shift:]+options[:shift]
                db.executemany('INSERT INTO comprehension_options VALUES (?,?,?,?)',[(qid,j,t,c) for j,(t,c) in enumerate(options)])
        for fr,en in p['expressions']:
            db.execute('INSERT INTO skill_expressions(unit_id,phrase_fr,meaning_en) VALUES (?,?,?)',(unit,fr,en))
            for direction,front,back in [('fr_en',fr,en),('en_fr',en,fr)]:
                db.execute('INSERT INTO flashcards(lesson_id,front,back,direction,tags_json) VALUES (?,?,?,?,?)',(days[2],front,back,direction,json.dumps(['weekly_context',level,f'unit_{unit}'])))
        prep = ('Plan using short clauses and words from the text. Check person, noun gender, agreement and the required information.' if level in ('A1','A2') else 'Outline the purpose, audience and logical sequence. Select examples; distinguish facts, interpretations and uncertainty. Revise reference, tense and register.')
        for kind in ('writing','speaking'):
            tid=db.execute('INSERT INTO production_tasks(unit_id,kind,prompt_en,preparation_en,auto_gradable) VALUES (?,?,?,?,0)',(unit,kind,p[kind],prep)).lastrowid
            criteria = [
                ('task','Respond to each requested point with relevant, concrete information. Suggested lengths are practice targets, not exam specifications.'),
                ('organisation','Use a clear sequence and unambiguous references.' if level in ('A1','A2') else 'Structure the argument or narrative; preserve source scope and distinguish your contribution.'),
                ('language','Check sentence order, agreement, tense and the weekly grammar focus: '+p['grammar']),
                ('communication','Use a suitable register and paraphrase missing words. '+('Pause at meaningful phrase boundaries; make contrasts audible and ask for clarification. No automatic pronunciation score is supplied.' if kind=='speaking' else 'Reread as the intended recipient; check whether any requested next action is clear.')),
            ]
            db.executemany('INSERT INTO production_rubrics VALUES (?,?,?)',[(tid,c,g) for c,g in criteria])
        for activity,day,minutes,instruction in [
            ('reading',2,12,'Read for the main point, then detail. Answer three questions before opening the evidence. Retrieve the contextual expressions.'),
            ('dialogue',3,10,'Read the six-turn script and answer two questions. Rehearse both roles, then change one constraint. This is listening preparation, not an audio assessment.'),
            ('writing',5,15,'Plan, write and revise using the task rubric. Keep a first draft to compare with your revision.'),
            ('speaking',6,12,'Prepare key words, speak without reading a full script, then ask a partner for feedback using the rubric.'),
            ('review',7,10,'Without the text, summarise the situation and retrieve three expressions. Revisit missed questions; revise one sentence and repeat the speaking task with a new detail.'),
        ]:
            db.execute('INSERT INTO skill_schedule VALUES (?,?,?,?,?)',(unit,days[day],activity,minutes,instruction))
        # Existing broad IPA/articulation guidance, not fabricated sentence-level IPA.
        rules=db.execute('SELECT id FROM pronunciation_rules WHERE introduced_day<=? ORDER BY introduced_day DESC,id LIMIT 2',(days[3],)).fetchall()
        for (rule,) in rules:
            db.execute('INSERT INTO skill_pronunciation VALUES (?,?,?)',(unit,rule,'Review this sound rule, mark meaningful phrase boundaries in two dialogue turns, and rehearse them slowly then at a comfortable pace. Use the existing word IPA guides; this script has no verified recording or full-sentence transcription.'))
