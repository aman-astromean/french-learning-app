#!/usr/bin/env python3
"""Export the SQLite course into static JSON used by the prototype UI."""
import json
import sqlite3
from pathlib import Path

HERE = Path(__file__).resolve().parent
DB = HERE.parent / 'french_course' / 'french_course.sqlite'
OUT = HERE / 'data'
OUT.mkdir(exist_ok=True)
connection = sqlite3.connect(DB)
connection.row_factory = sqlite3.Row

def rows(query, params=()):
    return [dict(row) for row in connection.execute(query, params)]

levels = rows('SELECT code,sequence,weeks,outcome FROM levels ORDER BY sequence')
units = rows('SELECT id,level_code,sequence,title,explanation FROM units ORDER BY sequence')
lessons = rows('SELECT id,unit_id,day_number,day_in_unit,kind,title,objective,estimated_minutes,example_fr,example_en FROM lessons ORDER BY day_number')
(OUT/'catalog.json').write_text(json.dumps({'levels':levels,'units':units,'lessons':lessons},ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
conversation=rows('SELECT rank,french,meaning_en,ipa,example_fr,example_en,example_status,example_source,conjugation_status,verb_id,introduced_day FROM conversation_words ORDER BY rank')
for entry in conversation:
    entry['conjugations']=rows('SELECT mood,tense,person,form FROM conjugations WHERE verb_id=? ORDER BY mood,tense,CASE person WHEN "je" THEN 1 WHEN "tu" THEN 2 WHEN "il/elle/on" THEN 3 WHEN "nous" THEN 4 WHEN "vous" THEN 5 ELSE 6 END',(entry['verb_id'],)) if entry['verb_id'] else []
(OUT/'conversation_words.json').write_text(json.dumps(conversation,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
verb_reference=[]
for verb in rows('SELECT v.*,r.infinitive_ipa,r.impersonal,r.auxiliary_note,r.agreement_note,r.usage_note,r.source_url FROM verbs v JOIN verb_reference r ON r.verb_id=v.id ORDER BY v.id'):
    vid=verb['id']
    forms=rows('SELECT c.mood,c.tense,c.person,c.form,p.ipa,p.status,p.word_parts_json FROM conjugations c JOIN conjugation_pronunciations p USING(verb_id,mood,tense,person) WHERE c.verb_id=? ORDER BY c.mood,c.tense,c.person',(vid,))
    verb['forms']=[[f['mood'],f['tense'],f['person'],f['form'],f['ipa'],f['status'],json.loads(f['word_parts_json'])] for f in forms]
    verb['variants']=rows('SELECT mood,tense,person,form,ipa,note FROM conjugation_variants WHERE verb_id=? ORDER BY mood,tense,person,form',(vid,))
    verb['participles']=rows('SELECT kind,agreement,form,ipa FROM verb_participles WHERE verb_id=? ORDER BY kind,agreement,form',(vid,))
    verb['coverage']=rows('SELECT mood,tense,status FROM conjugation_coverage WHERE verb_id=? ORDER BY mood,tense',(vid,))
    verb_reference.append(verb)
pronominal=rows('SELECT * FROM pronominal_verbs ORDER BY id')
for verb in pronominal:
    verb['forms']=rows('SELECT mood,tense,person,form,variants_json,note FROM pronominal_conjugations WHERE pronominal_verb_id=? ORDER BY mood,tense,person',(verb['id'],))
    for form in verb['forms']:form['variants']=json.loads(form.pop('variants_json'))
(OUT/'verb_reference.json').write_text(json.dumps({'form_columns':['mood','tense','person','form','ipa','pronunciation_status','word_parts'],'verbs':verb_reference,'pronominal_verbs':pronominal},ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
lexical_reference=[]
for word in rows('SELECT l.id,l.french,l.part_of_speech,l.gender,g.lemmas_json,g.parts_of_speech_json,g.genders_json,g.usage_note,p.phonemes_json,p.note,p.audio_status FROM lexemes l JOIN lexical_grammar g ON g.lexeme_id=l.id JOIN vocabulary_pronunciation p ON p.lexeme_id=l.id ORDER BY l.id'):
    for name in ('lemmas','parts_of_speech','genders','phonemes'):
        word[name]=json.loads(word.pop(name+'_json'))
    word['inflections']=rows('SELECT form,features,ipa FROM lexical_inflections WHERE lexeme_id=? ORDER BY form,features',(word['id'],))
    word['sentence_pattern_ids']=[r[0] for r in connection.execute('SELECT pattern_id FROM sentence_pattern_words WHERE lexeme_id=? ORDER BY pattern_id',(word['id'],))]
    lexical_reference.append(word)
(OUT/'lexical_reference.json').write_text(json.dumps(lexical_reference,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
sentence_patterns=rows('SELECT * FROM sentence_patterns ORDER BY id')
for pattern in sentence_patterns:
    pattern['components']=json.loads(pattern.pop('components_json'))
    pattern['tasks']=rows('SELECT id,kind,prompt,tokens_json,accepted_answers_json,explanation,auto_gradable FROM sentence_tasks WHERE pattern_id=? ORDER BY id',(pattern['id'],))
    for task in pattern['tasks']:
        task['tokens']=json.loads(task.pop('tokens_json'))
        task['accepted_answers']=json.loads(task.pop('accepted_answers_json'))
(OUT/'sentence_reference.json').write_text(json.dumps({'patterns':sentence_patterns,'phonemes':rows('SELECT * FROM phoneme_guides ORDER BY symbol'),'pronunciation_rules':rows('SELECT * FROM pronunciation_rules ORDER BY introduced_day,id')},ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
for level in levels:
    code=level['code']
    unit_ids=[unit['id'] for unit in units if unit['level_code']==code]
    lessons_for_level=[lesson for lesson in lessons if lesson['unit_id'] in unit_ids]
    ids=[lesson['id'] for lesson in lessons_for_level]
    payload={}
    for day in ids:
        blocks=rows('SELECT block_type,content_json FROM lesson_blocks WHERE lesson_id=? ORDER BY position',(day,))
        exercises=rows('SELECT id,kind,prompt,answer,explanation,auto_gradable,position FROM exercises WHERE lesson_id=? ORDER BY position',(day,))
        for exercise in exercises:
            exercise['choices']=rows('SELECT position,choice_text,correct FROM exercise_choices WHERE exercise_id=? ORDER BY position',(exercise['id'],))
        cards=rows('SELECT id,front,back,direction FROM flashcards WHERE lesson_id=? ORDER BY id',(day,))
        pronunciation=rows('SELECT category,grapheme,ipa,example_fr,example_ipa,meaning_en,articulation,contrast FROM pronunciation_items WHERE lesson_id=? ORDER BY position',(day,))
        vocabulary=rows('SELECT x.id,x.french,x.english,x.part_of_speech,x.gender,x.ipa,c.example_fr,c.example_en,c.example_status,c.verb_id FROM lesson_lexemes lx JOIN lexemes x ON x.id=lx.lexeme_id LEFT JOIN conversation_words c ON c.lexeme_id=x.id WHERE lx.lesson_id=? ORDER BY x.id',(day,))
        for word in vocabulary:
            word['present']=rows('SELECT c.person,c.form,p.ipa FROM conjugations c LEFT JOIN conjugation_pronunciations p USING(verb_id,mood,tense,person) WHERE c.verb_id=? AND c.mood="indicative" AND c.tense="present" ORDER BY CASE c.person WHEN "je" THEN 1 WHEN "tu" THEN 2 WHEN "il" THEN 3 WHEN "il/elle/on" THEN 3 WHEN "nous" THEN 4 WHEN "vous" THEN 5 ELSE 6 END',(word['verb_id'],)) if word['verb_id'] else []
        patterns=[p for p in sentence_patterns if p['introduced_day']==day]
        payload[str(day)]={'blocks':[{'type':b['block_type'],'data':json.loads(b['content_json'])} for b in blocks], 'exercises':exercises,'cards':cards,'pronunciation':pronunciation,'vocabulary':vocabulary,'sentence_patterns':patterns}
    (OUT/f'{code.lower()}.json').write_text(json.dumps(payload,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
connection.close()
print('Exported',len(lessons),'days and',len(units),'units')
