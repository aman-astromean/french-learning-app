"""Authored sentence construction, phoneme cues, and guided practice data."""
import csv
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parent

RULES=[
('liaison-determiner','A0','Determiner liaison','An otherwise silent final consonant is pronounced in common determiner + vowel-initial noun groups. The sound can differ from the spelling.','les amis','/lezami/',6),
('liaison-pronoun','A1','Subject-pronoun liaison','Liaison is expected between a subject pronoun and a following vowel-initial verb.','vous avez','/vuzave/',15),
('no-liaison-et','A1','No liaison after et','Do not insert a t sound after the conjunction et.','et elle','/e ɛl/',20),
('aspirated-h','A1','Aspirated h blocks linking','An aspirated h is normally silent but blocks elision and liaison. Check the dictionary: the written h alone does not identify the class.','un héros','/œ̃ eʁo/',26),
('mute-h','A1','Mute h permits elision','A mute h permits the same elision and liaison as a vowel-initial word.','l’hôtel','/lotɛl/',26),
('enchaînement','A1','Enchaînement','An already pronounced final consonant can join the following vowel; this is not the creation of a new liaison consonant.','une amie','/ynami/',27),
('elision','A0','Elision before a vowel','Words such as je, ne, le and la can lose their vowel before a vowel or mute h. Write the required apostrophe.','j’aime','/ʒɛm/',12),
('silent-final','A0','Silent final letters','Final written consonants are often silent, but lexical exceptions and inflections matter. Compare the dictionary forms.','petit / petite','/pəti/ ; /pətit/',5),
('nasal-oral','A0','Nasal versus oral vowel','A nasal vowel is not a vowel followed by a separate n. Doubling a nasal consonant can change the vowel to oral.','bon / bonne','/bɔ̃/ ; /bɔn/',6),
('rhythm-group','A2','Rhythm and prominence','French prominence generally falls near the end of a rhythmic group, not strongly on every individual word. Practise the phrase as a group.','un petit café','/œ̃ pəti kafe/',90),
('u-ou','A0','U and ou contrast','Keep the tongue forward for /y/ and back for /u/; both use rounded lips.','tu / tout','/ty/ ; /tu/',3),
('schwa','A2','Variable schwa','The presence of /ə/ depends on rhythm, region and neighbouring consonants. Learn a careful model before practising reductions.','samedi','/samədi/ ; /samdi/',91),
('plus-context','B1','Plus changes with context','Plus can be /ply/, /plys/ or /plyz/ depending on meaning, position and liaison. Do not apply one citation form everywhere.','deux plus deux','/dø plys dø/',160),
]

def dump(v):return json.dumps(v,ensure_ascii=False,separators=(',',':'))

def apply(conn):
    with (ROOT/'phoneme_guides.tsv').open(encoding='utf-8') as f:
        for row in csv.DictReader(f,delimiter='|'):
            conn.execute('INSERT INTO phoneme_guides VALUES (?,?,?,?,?,?)',tuple(row[k] for k in ['symbol','title','articulation','example_fr','example_ipa','contrast']))
    conn.executemany('INSERT INTO pronunciation_rules VALUES (?,?,?,?,?,?,?)',RULES)
    symbols=[r[0] for r in conn.execute('SELECT symbol FROM phoneme_guides')]
    symbols.sort(key=len,reverse=True)
    for lid,word,ipa in conn.execute('SELECT id,french,ipa FROM lexemes').fetchall():
        normalized=(ipa or '').replace('g','ɡ')
        phonemes=[];i=0
        while i<len(normalized):
            match=next((symbol for symbol in symbols if normalized.startswith(symbol,i)),None)
            if match:
                if match not in phonemes:phonemes.append(match)
                i+=len(match)
            else:i+=1
        note='The IPA is a citation pronunciation. Follow the linked sound cues; spelling does not map one-to-one to sounds. Connected speech, meaning, and regional accents can change the realization.'
        if any('̃' in p for p in phonemes):note+=' Nasal vowels do not automatically include a separate n or m sound.'
        conn.execute('INSERT INTO vocabulary_pronunciation(lexeme_id,phonemes_json,note) VALUES (?,?,?)',(lid,dump(phonemes),note))
    titles={};patterns=[]
    with (ROOT/'sentence_patterns.tsv').open(encoding='utf-8') as f:
        data=list(csv.DictReader(f,delimiter='|'))
    for pid,row in enumerate(data,1):
        components=[{'role':p.split(':',1)[0].strip(),'text':p.split(':',1)[1].strip()} for p in row['components'].split('^')]
        assembled=' '.join(c['text'] for c in components)
        assert assembled==row['example_fr'], (pid,assembled,row['example_fr'])
        day=int(row['day']);level=conn.execute('SELECT u.level_code FROM lessons l JOIN units u ON u.id=l.unit_id WHERE l.id=?',(day,)).fetchone()[0]
        assert level==row['level'],(pid,level,row['level'])
        conn.execute('INSERT INTO sentence_patterns VALUES (?,?,?,?,?,?,?,?,?,?)',(pid,level,row['title'],row['pattern'],row['explanation'],dump(components),row['example_fr'],row['example_en'],row['common_error'],day))
        titles[row['title']]=pid;patterns.append((pid,row))
        chunks=[c['text'] for c in components]
        conn.execute('INSERT INTO sentence_tasks(pattern_id,kind,prompt,tokens_json,accepted_answers_json,explanation,auto_gradable) VALUES (?,?,?,?,?,?,?)',(pid,'word_order',f'Rebuild this model sentence: {row["example_en"]} Follow: {row["pattern"]}.',dump(chunks[1:]+chunks[:1]),dump([row['example_fr']]),row['explanation']+' '+row['common_error'],1))
        conn.execute('INSERT INTO sentence_tasks(pattern_id,kind,prompt,tokens_json,accepted_answers_json,explanation,auto_gradable) VALUES (?,?,?,?,?,?,?)',(pid,'translation',f'Write and say a sentence expressing: {row["example_en"]}',dump([]),dump([row['example_fr']]),'The saved answer is a model. Other valid formulations need meaning-based review. '+row['common_error'],0))
    category={
        'noun':['Article and noun','Plural agreement','Location'],
        'verb':['Regular present statement','Present negation','Modal and infinitive'],
        'adjective':['Adjective agreement','Common adjective before a noun','Colour after the noun','Comparative adjective'],
        'adverb':['Regular present statement','Never','No longer'],
        'pronoun':['First statement','Direct object pronoun','Indirect object pronoun'],
        'preposition':['Location','À contractions','De contractions'],
        'determiner':['Article and noun','Possessive determiner'],
        'article':['Article and noun','Elision'],
        'numeral':['Age with avoir','Quantity with de'],
        'conjunction':['Giving a reason','Contrast with pourtant'],
        'connector':['Contrast with pourtant','Source comparison'],
        'interrogative':['Question word','Which noun'],
    }
    for lid,word,pos in conn.execute('SELECT id,french,part_of_speech FROM lexemes').fetchall():
        for title in category.get(pos,['First statement']):
            conn.execute('INSERT INTO sentence_pattern_words VALUES (?,?,?)',(titles[title],lid,'grammar_reference'))
        for pid,row in patterns:
            if re.search(r'(?<!\w)'+re.escape(word)+r'(?!\w)',row['example_fr'],re.I):
                conn.execute('INSERT INTO sentence_pattern_words VALUES (?,?,?) ON CONFLICT(pattern_id,lexeme_id) DO UPDATE SET link_type="example_use"',(pid,lid,'example_use'))
