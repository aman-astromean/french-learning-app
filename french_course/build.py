#!/usr/bin/env python3
"""Build a portable SQLite course seed from curriculum.tsv and schema.sql."""
import csv, json, sqlite3
from pathlib import Path
from expanded_content import apply as apply_expanded_content
from lexicon_growth import apply as apply_lexicon_growth
from conversation_growth import apply as apply_conversation_growth
ROOT=Path(__file__).resolve().parent
DB=ROOT/'french_course.sqlite'
if DB.exists(): DB.unlink()
conn=sqlite3.connect(DB)
conn.executescript((ROOT/'schema.sql').read_text())
levels=[('A0',0,2,'Recognize French print and sounds; greet and exchange very basic information.'),('A1',1,10,'Introduce yourself and handle predictable everyday interactions.'),('A2',2,10,'Manage routine transactions and describe past experiences and plans.'),('B1',3,12,'Narrate, explain opinions, and handle familiar social and professional situations.'),('B2',4,10,'Argue a position, summarize sources, and interact confidently across topics.'),('C1',5,8,'Communicate fluently with control of register, implication, and complex organization.'),('C2',6,8,'Express and interpret fine shades of meaning in demanding communication.')]
conn.executemany('INSERT INTO levels VALUES (?,?,?,?)',levels)
rows=[]
for number,line in enumerate((ROOT/'curriculum.tsv').read_text().splitlines(),1):
    parts=line.split('|')
    assert len(parts)==9,(number,len(parts))
    level,title,note,*items=parts
    assert level in {x[0] for x in levels}
    topics=[]
    for item in items:
        sub=item.split('^')
        assert len(sub)==3,(number,item)
        topics.append(sub)
    rows.append((level,title,note,topics))
assert len(rows)==60
for code,_,weeks,_ in levels: assert sum(r[0]==code for r in rows)==weeks
for week,(level,title,note,topics) in enumerate(rows,1):
    conn.execute('INSERT INTO units VALUES (?,?,?,?,?)',(week,level,week,title,note))
    for slot,(topic,fr,en) in enumerate(topics,1):
        day=(week-1)*7+slot
        conn.execute('INSERT INTO lessons VALUES (?,?,?,?,?,?,?,?,?,?)',(day,week,day,slot,'learn',topic,f'{note} Practice: {topic.lower()}.',18 if level in ('A0','A1') else 25 if level in ('A2','B1') else 35,fr,en))
        conn.execute('INSERT INTO grammar_topics VALUES (?,?,?,?,?,?)',(day,week,topic,note,fr,en))
        conn.execute('INSERT INTO lesson_grammar VALUES (?,?)',(day,day))
        blocks=[('explanation',{'text':note,'focus':topic}),('example',{'french':fr,'english':en}),('production',{'instruction':f'Use the expression from “{topic}” in your own situation. Say it aloud and write one sentence.','model':fr})]
        for position,(kind,data) in enumerate(blocks,1): conn.execute('INSERT INTO lesson_blocks(lesson_id,position,block_type,content_json) VALUES (?,?,?,?)',(day,position,kind,json.dumps(data,ensure_ascii=False)))
        tags=json.dumps([level,title,topic],ensure_ascii=False)
        for direction,front,back in [('fr_en',fr,en),('en_fr',en,fr)]: conn.execute('INSERT INTO flashcards(lesson_id,front,back,direction,tags_json) VALUES (?,?,?,?,?)',(day,front,back,direction,tags))
        choices=[en,topics[(slot)%6][2],topics[(slot+1)%6][2]]
        assert len(set(choices))==3
        choices=choices[day%3:]+choices[:day%3]
        cur=conn.execute('INSERT INTO exercises(lesson_id,kind,prompt,answer,explanation,auto_gradable,position) VALUES (?,?,?,?,?,?,?)',(day,'choice',f'Choose the meaning of: {fr}',en,f'“{fr}” means “{en}”.',1,1))
        for pos,choice in enumerate(choices,1): conn.execute('INSERT INTO exercise_choices VALUES (?,?,?,?)',(cur.lastrowid,pos,choice,int(choice==en)))
        # A full French sentence as a text answer avoids false certainty about context-dependent spelling.
        conn.execute('INSERT INTO exercises(lesson_id,kind,prompt,answer,explanation,auto_gradable,position) VALUES (?,?,?,?,?,?,?)',(day,'production',f'Translate into French, then speak it aloud: {en}',fr,'Compare your response with the model. Alternative valid translations need human or rubric-based evaluation.',0,2))
        if day>1: conn.execute('INSERT INTO lesson_prerequisites VALUES (?,?)',(day,day-1))
    day=week*7
    conn.execute('INSERT INTO lessons VALUES (?,?,?,?,?,?,?,?,?,?)',(day,week,day,7,'review',f'Review: {title}',f'Retrieve this week’s six expressions, then perform a {level} speaking or writing task.',25 if level in ('A0','A1') else 40,None,None))
    conn.execute('INSERT INTO lesson_blocks(lesson_id,position,block_type,content_json) VALUES (?,?,?,?)',(day,1,'review',json.dumps({'steps':['Recall all six expressions without looking.','Review missed flashcards.','Record or write a short response using at least three expressions.','Complete the six-question checkpoint.'],'pass_threshold':0.8,'promotion_requires_external_assessment':level in ('B2','C1','C2')},ensure_ascii=False)))
    for slot,(topic,fr,en) in enumerate(topics,1):
        distractors=[topics[(slot)%6][2],topics[(slot+1)%6][2]]
        cur=conn.execute('INSERT INTO exercises(lesson_id,kind,prompt,answer,explanation,auto_gradable,position) VALUES (?,?,?,?,?,?,?)',(day,'choice',f'Weekly checkpoint — translate: {fr}',en,f'Revisit day {(week-1)*7+slot}: {topic}.',1,slot))
        options=[en]+distractors
        options=options[(day+slot)%3:]+options[:(day+slot)%3]
        for pos,choice in enumerate(options,1): conn.execute('INSERT INTO exercise_choices VALUES (?,?,?,?)',(cur.lastrowid,pos,choice,int(choice==en)))
    conn.execute('INSERT INTO exercises(lesson_id,kind,prompt,answer,explanation,auto_gradable,position) VALUES (?,?,?,?,?,?,?)',(day,'production',f'Speak for 60–180 seconds or write 80–250 words about “{title}”. Use at least three of this week’s expressions.',None,'Evaluate meaning, intelligibility, grammatical control, and register with level-appropriate rubrics.',0,7))
    conn.execute('INSERT INTO lesson_prerequisites VALUES (?,?)',(day,day-1))
    if week<60: pass
# Link the first day of each later week to the prior review.
# Alphabet: IPA denotes the name of the letter, not its invariant sound in words.
alphabet=[('a','/a/','ami'),('bé','/be/','bébé'),('cé','/se/','café'),('dé','/de/','deux'),('e','/ə/','le'),('effe','/ɛf/','fille'),('gé','/ʒe/','gare'),('ache','/aʃ/','hôtel'),('i','/i/','ici'),('ji','/ʒi/','jour'),('ka','/ka/','kilo'),('elle','/ɛl/','livre'),('emme','/ɛm/','mère'),('enne','/ɛn/','nuit'),('o','/o/','orange'),('pé','/pe/','père'),('ku','/ky/','qui'),('erre','/ɛʁ/','rue'),('esse','/ɛs/','sac'),('té','/te/','table'),('u','/y/','une'),('vé','/ve/','ville'),('double vé','/dublə ve/','wagon'),('iks','/iks/','taxi'),('i grec','/i ɡʁɛk/','yoga'),('zède','/zɛd/','zéro')]
for i,(name,ipa,example) in enumerate(alphabet): conn.execute('INSERT INTO alphabet VALUES (?,?,?,?)',(chr(65+i),name,ipa,example))
patterns=[('é','/e/','été','Closed e; accent aigu.'),('è','/ɛ/','père','Open e; accent grave.'),('ê','/ɛ/','fête','Often open e; accent circonflexe.'),('ç','/s/','garçon','Makes c soft before a, o, or u.'),('ou','/u/','vous','Rounded back vowel.'),('u','/y/','tu','Rounded front vowel; contrast with ou.'),('on','/ɔ̃/','bon','Nasal vowel in many contexts.'),('an/en','/ɑ̃/','enfant','Common nasal vowel; spelling varies.'),('in/ain','/ɛ̃/','pain','Common nasal vowel; regional variation exists.'),('ch','/ʃ/','chat','Usually sh sound.'),('gn','/ɲ/','montagne','Palatal nasal.'),('oi','/wa/','moi','Often pronounced wa.'),('eu','/ø/','deux','Rounded vowel; changes across contexts.'),('ill','/j/','fille','Common pattern; exceptions include ville.'),('liaison','/z/','vous avez','Linking sound in common liaison contexts.'),('silent ending','∅','petit','Many final consonants are silent; exceptions apply.'),('r','/ʁ/','rue','Common metropolitan pronunciation; regional variation exists.')]
conn.executemany('INSERT INTO sound_patterns(spelling,ipa,example,note) VALUES (?,?,?,?)',patterns)
base=['zéro','un','deux','trois','quatre','cinq','six','sept','huit','neuf','dix','onze','douze','treize','quatorze','quinze','seize','dix-sept','dix-huit','dix-neuf']
tens={20:'vingt',30:'trente',40:'quarante',50:'cinquante',60:'soixante'}
def french_num(n):
    if n<20: return base[n]
    if n==100: return 'cent'
    if n>=80:
        if n==80: return 'quatre-vingts'
        return 'quatre-vingt-'+(french_num(n-80) if n!=81 else 'un')
    if n>=70: return 'soixante-'+french_num(n-60) if n!=71 else 'soixante et onze'
    t=(n//10)*10; r=n-t
    if r==0: return tens[t]
    if r==1: return tens[t]+' et un'
    return tens[t]+'-'+base[r]
for n in range(101): conn.execute('INSERT INTO numbers VALUES (?,?,?)',(n,french_num(n),str(n)))
verbs={
'être':('be','irregular','avoir','A0',['suis','es','est','sommes','êtes','sont']),
'avoir':('have','irregular','avoir','A0',['ai','as','a','avons','avez','ont']),
'aller':('go','irregular','être','A1',['vais','vas','va','allons','allez','vont']),
'faire':('do/make','irregular','avoir','A1',['fais','fais','fait','faisons','faites','font']),
'parler':('speak','-er','avoir','A1',['parle','parles','parle','parlons','parlez','parlent']),
'finir':('finish','-ir','avoir','A2',['finis','finis','finit','finissons','finissez','finissent']),
'prendre':('take','irregular','avoir','A2',['prends','prends','prend','prenons','prenez','prennent']),
'venir':('come','irregular','être','A2',['viens','viens','vient','venons','venez','viennent']),
'pouvoir':('be able to','irregular','avoir','A2',['peux','peux','peut','pouvons','pouvez','peuvent']),
'vouloir':('want','irregular','avoir','A2',['veux','veux','veut','voulons','voulez','veulent']),
'devoir':('have to','irregular','avoir','A2',['dois','dois','doit','devons','devez','doivent']),
'savoir':('know (a fact/how)','irregular','avoir','B1',['sais','sais','sait','savons','savez','savent']),
}
persons=['je','tu','il/elle/on','nous','vous','ils/elles']
for vid,(inf,(english,group,aux,level,forms)) in enumerate(verbs.items(),1):
    conn.execute('INSERT INTO verbs VALUES (?,?,?,?,?,?)',(vid,inf,english,group,aux,level))
    for person,form in zip(persons,forms): conn.execute('INSERT INTO conjugations VALUES (?,?,?,?,?)',(vid,'indicative','present',person,form))
# Irregular stems and stems shared by transparent -er formation.
tense_forms={
'être':{'imperfect':['étais','étais','était','étions','étiez','étaient'],'future':['serai','seras','sera','serons','serez','seront'],'conditional':['serais','serais','serait','serions','seriez','seraient'],'subjunctive_present':['sois','sois','soit','soyons','soyez','soient']},
'avoir':{'imperfect':['avais','avais','avait','avions','aviez','avaient'],'future':['aurai','auras','aura','aurons','aurez','auront'],'conditional':['aurais','aurais','aurait','aurions','auriez','auraient'],'subjunctive_present':['aie','aies','ait','ayons','ayez','aient']},
'aller':{'imperfect':['allais','allais','allait','allions','alliez','allaient'],'future':['irai','iras','ira','irons','irez','iront'],'conditional':['irais','irais','irait','irions','iriez','iraient'],'subjunctive_present':['aille','ailles','aille','allions','alliez','aillent']},
'faire':{'imperfect':['faisais','faisais','faisait','faisions','faisiez','faisaient'],'future':['ferai','feras','fera','ferons','ferez','feront'],'conditional':['ferais','ferais','ferait','ferions','feriez','feraient'],'subjunctive_present':['fasse','fasses','fasse','fassions','fassiez','fassent']},
'parler':{'imperfect':['parlais','parlais','parlait','parlions','parliez','parlaient'],'future':['parlerai','parleras','parlera','parlerons','parlerez','parleront'],'conditional':['parlerais','parlerais','parlerait','parlerions','parleriez','parleraient'],'subjunctive_present':['parle','parles','parle','parlions','parliez','parlent']},
'finir':{'imperfect':['finissais','finissais','finissait','finissions','finissiez','finissaient'],'future':['finirai','finiras','finira','finirons','finirez','finiront'],'conditional':['finirais','finirais','finirait','finirions','finiriez','finiraient'],'subjunctive_present':['finisse','finisses','finisse','finissions','finissiez','finissent']},
}
for inf,tenses in tense_forms.items():
    vid=list(verbs).index(inf)+1
    for tense,forms in tenses.items():
        mood='subjunctive' if tense=='subjunctive_present' else 'indicative' if tense in ('imperfect','future') else 'conditional'
        name='present' if tense=='subjunctive_present' else tense
        for person,form in zip(persons,forms): conn.execute('INSERT INTO conjugations VALUES (?,?,?,?,?)',(vid,mood,name,person,form))
# Predictable -er and regular -ir paradigms are generated from explicit, vetted
# group membership. Spelling-changing and irregular verbs require separate review.
regular_verbs={
'aimer':'like','habiter':'live','regarder':'watch','écouter':'listen','travailler':'work','visiter':'visit','demander':'ask','donner':'give','montrer':'show','trouver':'find','chercher':'look for','marcher':'walk','chanter':'sing','danser':'dance','entrer':'enter','porter':'wear or carry','penser':'think','étudier':'study','préparer':'prepare','présenter':'present','expliquer':'explain','décider':'decide','organiser':'organize','comparer':'compare','réserver':'reserve','inviter':'invite','accepter':'accept','refuser':'refuse','continuer':'continue','terminer':'finish','oublier':'forget','utiliser':'use','rencontrer':'meet','aider':'help','jouer':'play','téléphoner':'call','souhaiter':'wish','proposer':'propose','imaginer':'imagine','respecter':'respect','raconter':'tell','observer':'observe','dessiner':'draw','déjeuner':'have lunch','dîner':'have dinner','apporter':'bring','emporter':'take away','arriver':'arrive','rester':'stay','quitter':'leave','poser':'put down or ask','cacher':'hide','gagner':'win','parier':'bet',
'choisir':'choose','réussir':'succeed','grandir':'grow','remplir':'fill','réfléchir':'reflect','rougir':'blush','grossir':'gain weight','maigrir':'lose weight','ralentir':'slow down','vieillir':'grow old','obéir':'obey','punir':'punish','bâtir':'build','nourrir':'feed','guérir':'heal','atterrir':'land'}
endings={'present':(['e','es','e','ons','ez','ent'],['is','is','it','issons','issez','issent']),'imperfect':(['ais','ais','ait','ions','iez','aient'],['issais','issais','issait','issions','issiez','issaient']),'future':(['ai','as','a','ons','ez','ont'],['ai','as','a','ons','ez','ont']),'conditional':(['ais','ais','ait','ions','iez','aient'],['ais','ais','ait','ions','iez','aient'])}
for inf,english in regular_verbs.items():
    if inf in verbs: continue
    group='-er' if inf.endswith('er') else '-ir'
    assert group=='-er' or inf.endswith('ir')
    level='A1' if inf in {'aimer','habiter','regarder','écouter','travailler','visiter','demander','donner','chercher','marcher','chanter','danser','entrer','porter','jouer'} else 'A2' if group=='-er' or inf in {'choisir','réussir','grandir','remplir'} else 'B1'
    cur=conn.execute('INSERT INTO verbs(infinitive,english,group_name,auxiliary,level_code) VALUES (?,?,?,?,?)',(inf,english,group,'être' if inf in {'entrer','arriver','rester'} else 'avoir',level))
    for tense,(er_endings,ir_endings) in endings.items():
        stem=inf if tense in ('future','conditional') else inf[:-2]
        suffixes=er_endings if group=='-er' else ir_endings
        for person,suffix in zip(persons,suffixes):
            conn.execute('INSERT INTO conjugations VALUES (?,?,?,?,?)',(cur.lastrowid,'conditional' if tense=='conditional' else 'indicative','present' if tense=='conditional' else tense,person,stem+suffix))
# High-value lemma inventory, including noun gender. Sentences remain separate phrase flashcards.
lexicon='''bonjour~hello~interjection~|merci~thank you~interjection~|oui~yes~adverb~|non~no~adverb~|au revoir~goodbye~expression~|s’il vous plaît~please~expression~|ami~friend~noun~m|amie~friend~noun~f|homme~man~noun~m|femme~woman~noun~f|enfant~child~noun~m|livre~book~noun~m|maison~house~noun~f|table~table~noun~f|école~school~noun~f|ville~city~noun~f|jour~day~noun~m|nuit~night~noun~f|matin~morning~noun~m|soir~evening~noun~m|semaine~week~noun~f|année~year~noun~f|temps~time/weather~noun~m|heure~hour~noun~f|eau~water~noun~f|pain~bread~noun~m|café~coffee/café~noun~m|thé~tea~noun~m|repas~meal~noun~m|restaurant~restaurant~noun~m|gare~station~noun~f|train~train~noun~m|billet~ticket~noun~m|rue~street~noun~f|travail~work~noun~m|emploi~job~noun~m|famille~family~noun~f|mère~mother~noun~f|père~father~noun~m|frère~brother~noun~m|sœur~sister~noun~f|voiture~car~noun~f|vélo~bicycle~noun~m|problème~problem~noun~m|solution~solution~noun~f|question~question~noun~f|réponse~answer~noun~f|idée~idea~noun~f|avis~opinion~noun~m|fait~fact~noun~m|preuve~evidence~noun~f|source~source~noun~f|donnée~data point~noun~f|argument~argument~noun~m|accord~agreement~noun~m|désaccord~disagreement~noun~m|grand~big/tall~adjective~|petit~small~adjective~|bon~good~adjective~|mauvais~bad~adjective~|beau~beautiful~adjective~|nouveau~new~adjective~|important~important~adjective~|possible~possible~adjective~|difficile~difficult~adjective~|facile~easy~adjective~|heureux~happy~adjective~|triste~sad~adjective~|ici~here~adverb~|là~there~adverb~|toujours~always~adverb~|souvent~often~adverb~|parfois~sometimes~adverb~|jamais~never~adverb~|aujourd’hui~today~adverb~|demain~tomorrow~adverb~|hier~yesterday~adverb~|avec~with~preposition~|sans~without~preposition~|dans~in~preposition~|sur~on~preposition~|sous~under~preposition~|chez~at someone’s place~preposition~|pour~for~preposition~|contre~against~preposition~|avant~before~preposition~|après~after~preposition~|parce que~because~conjunction~|cependant~however~connector~|néanmoins~nevertheless~connector~|en revanche~on the other hand~connector~'''
for i,row in enumerate(lexicon.split('|'),1):
    if not row: continue
    fr,en,pos,gender=row.split('~')
    level='A1' if i<=55 else 'A2' if i<=85 else 'B1'
    cur=conn.execute('INSERT INTO lexemes(french,english,part_of_speech,gender,level_code) VALUES (?,?,?,?,?)',(fr,en,pos,gender or None,level))
    # Introduce core lemmas gradually at their level, rather than dumping all
    # A1 words into an A0 lesson or all A2 words on its first day.
    lesson=(15+((i-1)*2)%70) if level=='A1' else (85+((i-56)*2)%70) if level=='A2' else (155+((i-86)*2)%84)
    for direction,front,back in [('fr_en',fr,en),('en_fr',en,fr)]: conn.execute('INSERT INTO flashcards(lesson_id,lexeme_id,front,back,direction,tags_json) VALUES (?,?,?,?,?,?)',(lesson,cur.lastrowid,front,back,direction,json.dumps(['core_vocabulary',level])))
    conn.execute('INSERT INTO lesson_lexemes VALUES (?,?)',(lesson,cur.lastrowid))
apply_lexicon_growth(conn)
for line in (ROOT/'reference_notes.tsv').read_text().splitlines():
    values=line.split('|')
    assert len(values)==6,(len(values),line)
    conn.execute('INSERT INTO reference_notes(level_code,category,title,explanation,example_fr,example_en) VALUES (?,?,?,?,?,?)',values)
conn.execute('INSERT INTO voice_integrations(name,repository_url,pinned_commit,capability,integration_status,french_verified,notes) VALUES (?,?,?,?,?,?,?)',('BernieTv ElevenLabs-Clone','https://github.com/BernieTv/ElevenLabs-Clone.git','5c3aff322c172ae714c57e930057065982f9f8a8','text_to_speech,voice_conversion,sound_effects','candidate',0,'French synthesis and speech assessment unverified; see VOICE_INTEGRATION.md'))
apply_expanded_content(conn)
apply_conversation_growth(conn)
conn.commit()
checks={
'levels':7,'units':60,'lessons':420,'learn_lessons':360,'review_lessons':60,'grammar_topics':360,'alphabet':26,'numbers':101,'conversation_words':1000,'reference_notes':67,'voice_integrations':1,'content_sources':5}
for table,expected in checks.items():
    actual=conn.execute(f'SELECT COUNT(*) FROM {table}' if table not in ('learn_lessons','review_lessons') else f"SELECT COUNT(*) FROM lessons WHERE kind='{'learn' if table=='learn_lessons' else 'review'}'").fetchone()[0]
    assert actual==expected,(table,actual,expected)
assert not conn.execute('PRAGMA foreign_key_check').fetchall()
assert conn.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
assert not conn.execute('SELECT exercise_id FROM exercise_choices GROUP BY exercise_id HAVING SUM(correct)!=1 OR COUNT(*)!=3').fetchall()
assert conn.execute('SELECT COUNT(*) FROM lessons WHERE example_fr IS NULL AND kind="learn"').fetchone()[0]==0
assert conn.execute('SELECT COUNT(*) FROM pronunciation_items').fetchone()[0]>=50
assert conn.execute('SELECT COUNT(*) FROM exercises').fetchone()[0]>1800
assert not conn.execute('SELECT rank FROM conversation_words WHERE trim(meaning_en)="" OR trim(ipa)="" OR trim(example_fr)="" OR trim(example_en)=""').fetchall()
assert not conn.execute("SELECT rank FROM conversation_words WHERE conjugation_status='available' AND verb_id IS NULL").fetchall()
assert not conn.execute("SELECT c.rank FROM conversation_words c LEFT JOIN conjugations f ON f.verb_id=c.verb_id AND f.mood='indicative' AND f.tense='present' WHERE c.conjugation_status='available' GROUP BY c.rank HAVING COUNT(f.person)!=6").fetchall()
cur=conn.execute('SELECT day_number,level,unit_title,kind,title,objective,estimated_minutes,example_fr,example_en FROM daily_course')
with (ROOT/'course_days.csv').open('w',newline='',encoding='utf-8') as output:
    writer=csv.writer(output)
    writer.writerow([column[0] for column in cur.description])
    writer.writerows(cur)
conn.close()
print('Built',DB,'with',checks)
