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
conversation=rows('SELECT rank,french,meaning_en,ipa,example_fr,example_en,example_status,conjugation_status,verb_id,introduced_day FROM conversation_words ORDER BY rank')
for entry in conversation:
    entry['conjugations']=rows('SELECT mood,tense,person,form FROM conjugations WHERE verb_id=? ORDER BY mood,tense,CASE person WHEN "je" THEN 1 WHEN "tu" THEN 2 WHEN "il/elle/on" THEN 3 WHEN "nous" THEN 4 WHEN "vous" THEN 5 ELSE 6 END',(entry['verb_id'],)) if entry['verb_id'] else []
(OUT/'conversation_words.json').write_text(json.dumps(conversation,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
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
        vocabulary=rows('SELECT x.french,x.english,x.part_of_speech,x.gender,x.ipa FROM lesson_lexemes lx JOIN lexemes x ON x.id=lx.lexeme_id WHERE lx.lesson_id=? ORDER BY x.id',(day,))
        payload[str(day)]={'blocks':[{'type':b['block_type'],'data':json.loads(b['content_json'])} for b in blocks], 'exercises':exercises,'cards':cards,'pronunciation':pronunciation,'vocabulary':vocabulary}
    (OUT/f'{code.lower()}.json').write_text(json.dumps(payload,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
connection.close()
print('Exported',len(lessons),'days and',len(units),'units')
