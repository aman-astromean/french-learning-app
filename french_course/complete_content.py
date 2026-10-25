"""Complete the existing vocabulary bank from checked-in linguistic references.

Lefff-derived morphology remains LGPL-LR (licenses/Lefff-LGPL-LR.txt).
Examples remain explicitly unreviewed; no human approval or recordings are implied.
"""
import csv
import json
from collections import defaultdict
from pathlib import Path
from reflexive_content import ROUTINES, apply as apply_pronominal_content

ROOT=Path(__file__).resolve().parent
SOURCE='https://github.com/RosaeNLG/rosaenlg/blob/master/packages/french-verbs-lefff/resources/lefff-3.4.mlex'
PERSONS=['je','tu','il/elle/on','nous','vous','ils/elles']
ETRE=set('aller venir devenir revenir parvenir intervenir survenir arriver entrer rentrer retourner rester partir sortir monter descendre tomber mourir naître apparaître remonter souvenir'.split())
DUAL=set('entrer rentrer retourner sortir monter descendre passer remonter paraître apparaître disparaître demeurer convenir'.split())
# The IPA dictionary combines unrelated homographs. Select the verb reading.
VERB_IPA={
    ('accepter','acceptions'):'/aksɛptjɔ̃/',('adopter','adoptions'):'/adɔptjɔ̃/',
    ('avoir','aura'):'/oʁa/',('avoir','auras'):'/oʁa/',('avoir','as'):'/a/',
    ('boire','but'):'/by/',('fermer','ferment'):'/fɛʁm/',
    ('inspecter','inspections'):'/ɛ̃spɛktjɔ̃/',('inventer','inventions'):'/ɛ̃vɑ̃tjɔ̃/',
    ('lire','lis'):'/li/',('plaire','plus'):'/ply/',('porter','portions'):'/pɔʁtjɔ̃/',
    ('presser','pressent'):'/pʁɛs/',('rater','rations'):'/ʁatjɔ̃/',
    ('savoir','sus'):'/sy/',('sentir','sens'):'/sɑ̃/',
    ('vivre','vis'):'/vi/',('voir','vis'):'/vi/',('être','est'):'/ɛ/',
}
GENDER_BY_SENSE={
    **dict.fromkeys('mort ombre part fin œuvre mémoire somme gauche aide poche crème critique cave finale vague barbe manche boum foudre vapeur bulle poêle'.split(),'f'),
    **dict.fromkeys('geste espace manque champagne classique plastique basket boucher aigle pompier vase évènement'.split(),'m'),
}
SENSE_NOTES={
    'tour':'Le tour = turn/tour; la tour = tower. Gender follows the selected sense.',
    'mémoire':'La mémoire = memory; un mémoire = a written report or dissertation.',
    'manche':'La manche = sleeve/round; le manche = handle.',
    'poêle':'La poêle = frying pan; le poêle = stove.',
    'vase':'Le vase = vase; la vase = mud/silt.',
    'œuvre':'Usually une œuvre for a work of art; some collective or technical senses use masculine.',
}
SENSE_FIXES={
    'capable':('adjective','capable; able','Elle est capable de résoudre ce problème.','She is able to solve this problem.'),
    'égoïste':('adjective','selfish','Ce comportement est égoïste.','This behaviour is selfish.'),
    'manque':('noun','lack; shortage','Le manque de sommeil me fatigue.','Lack of sleep makes me tired.'),
    'casse':('noun','breakage; damage','Cette boîte protège le verre contre la casse.','This box protects the glass against breakage.'),
    'batterie':('noun','battery; drum kit','La batterie de mon téléphone est vide.','My phone battery is flat.'),
    'cinquième':('numeral','fifth','Elle habite au cinquième étage.','She lives on the fifth floor.'),
    'septième':('numeral','seventh','C’est le septième jour du voyage.','It is the seventh day of the trip.'),
    'chine':('proper_noun','China','La Chine est située en Asie.','China is in Asia.'),
}
USAGE={
    'souvenir':'Use se souvenir de in modern everyday French. Bare source stems require a reflexive pronoun; use the dedicated se souvenir reference for complete pronominal forms.',
    'falloir':'Impersonal: use il faut / il fallait / il faudra. Follow with an infinitive or que + subjunctive. Do not invent je or tu forms.',
    'pouvoir':'Modal: subject + conjugated pouvoir + bare infinitive: Je peux venir. Puis-je is a formal inversion variant of je peux.',
    'devoir':'Modal: subject + conjugated devoir + bare infinitive: Je dois partir. The noun devoir means duty or homework.',
    'vouloir':'Subject + conjugated vouloir + noun or bare infinitive: Je veux un café; je veux partir.',
    'savoir':'Savoir + noun/que-clause or bare infinitive for a learned skill: Je sais nager. Connaître is used for familiarity with people and places.',
    'commencer':'Commencer à + infinitive: Je commence à comprendre.',
    'continuer':'Continuer à/de + infinitive: Elle continue à travailler.',
    'finir':'Finir de + infinitive: Je finis de manger.',
    'arrêter':'Arrêter + direct object; arrêter de + infinitive. Se arrêter becomes s’arrêter in the reflexive construction.',
    'décider':'Décider de + infinitive: Nous décidons de partir.',
    'essayer':'Essayer de + infinitive: Essaie de comprendre.',
    'éviter':'Éviter de + infinitive: Évite de courir ici.',
    'oublier':'Oublier de + infinitive: Je n’oublie pas de répondre.',
    'permettre':'Permettre à quelqu’un de + infinitive: Cela me permet de travailler.',
    'empêcher':'Empêcher quelqu’un de + infinitive: Le bruit m’empêche de dormir.',
    'obliger':'Obliger quelqu’un à + infinitive: La pluie nous oblige à rentrer.',
    'demander':'Demander quelque chose à quelqu’un; demander à quelqu’un de + infinitive.',
    'parler':'Parler à quelqu’un; parler de quelque chose. Je parle à Léa; je lui parle.',
    'téléphoner':'Téléphoner à quelqu’un: Je téléphone à Paul; je lui téléphone.',
    'répondre':'Répondre à une personne ou à une question: Je réponds à Léa; je lui réponds.',
    'penser':'Penser à + person/thing; penser de for an opinion: Que penses-tu de ce film ?',
    'rêver':'Rêver de + noun/infinitive: Je rêve de voyager.',
    'manquer':'Manquer à quelqu’un reverses the English perspective: Tu me manques = I miss you.',
    'plaire':'Plaire à quelqu’un: Ce livre me plaît = I like this book.',
    'aider':'Aider quelqu’un à + infinitive: Je l’aide à comprendre.',
    'apprendre':'Apprendre à + infinitive; apprendre quelque chose à quelqu’un.',
    'attendre':'Attendre quelqu’un/quelque chose takes a direct object: J’attends le bus.',
    'écouter':'Écouter quelqu’un/quelque chose takes a direct object: J’écoute la radio.',
    'regarder':'Regarder quelqu’un/quelque chose takes a direct object: Je regarde le film.',
    'chercher':'Chercher quelqu’un/quelque chose takes a direct object: Je cherche mes clés.',
    'habiller':'Habiller quelqu’un = dress someone. S’habiller = get dressed; use être in reflexive compound tenses.',
    'lever':'Lever un objet = raise an object. Se lever = get up; use être in reflexive compound tenses.',
    'réveiller':'Réveiller quelqu’un = wake someone. Se réveiller = wake up; use être in reflexive compound tenses.',
    'coucher':'Coucher quelqu’un = put someone to bed. Se coucher = go to bed.',
    'soucier':'Usually se soucier de: Je me soucie de toi. The bare finite reference needs reflexive pronouns in this use.',
    'taire':'Taire quelque chose = keep something quiet. Se taire = stop speaking.',
}

def dump(value):return json.dumps(value,ensure_ascii=False,separators=(',',':'))

def apply(conn):
    ref=json.loads((ROOT/'completion_reference.json').read_text())
    words=conn.execute('SELECT id,french,part_of_speech,gender FROM lexemes ORDER BY id').fetchall()
    for lid,word,old_pos,old_gender in words:
        lex=ref['lexical'][word];pos=SENSE_FIXES[word][0] if word in SENSE_FIXES else lex['primary_pos']
        gender=GENDER_BY_SENSE.get(word) or old_gender or (lex['genders'][0] if pos=='noun' and len(lex['genders'])==1 else None)
        if pos!='noun':gender=None
        conn.execute('UPDATE lexemes SET part_of_speech=?,gender=? WHERE id=?',(pos,gender,lid))
        note='A word can have more than one part of speech or sense. Morphology features: m/f = gender; s/p = number. '
        if len(lex['genders'])>1:note+='Gender depends on the sense or referent; use the article and context. '
        if word=='souvenir':note+='Souvenir is the noun memory/souvenir. To remember is se souvenir de, a reflexive verb. '
        if word=='est':note+='This entry means east /ɛst/. The être form est is /ɛ/; do not interchange these pronunciations. '
        if word=='plus':note+='Pronunciation depends on negation, comparison, emphasis, and liaison; a citation IPA is not a universal sentence pronunciation. '
        note+=SENSE_NOTES.get(word,'')
        conn.execute('INSERT INTO lexical_grammar VALUES (?,?,?,?,?,?)',(lid,dump(lex['lemmas']),dump(sorted(set(lex['parts_of_speech']+[pos]))),dump(lex['genders']),note,SOURCE))
        for form,features,ipa in lex['forms']:
            conn.execute('INSERT OR IGNORE INTO lexical_inflections VALUES (?,?,?,?)',(lid,form,features,ipa))

    # Replace the incomplete/generated tense inventory with source-backed cells.
    conn.execute('DELETE FROM conjugations')
    ids={w:vid for vid,w in conn.execute('SELECT id,infinitive FROM verbs')}
    for word,source in ref['verbs'].items():
        if word not in ids:
            row=conn.execute('SELECT english,level_code FROM lexemes WHERE french=?',(word,)).fetchone()
            english,level=(row[0].removeprefix('to '),row[1]) if row else (ROUTINES[word][1],'A2')
            if word=='souvenir':english='remember (se souvenir de)'
            cur=conn.execute('INSERT INTO verbs(infinitive,english,group_name,auxiliary,level_code) VALUES (?,?,?,?,?)',(word,english,'Lefff reference','être' if word in ETRE else 'avoir',level))
            ids[word]=cur.lastrowid
        vid=ids[word];aux='être' if word in ETRE else 'avoir'
        conn.execute('UPDATE verbs SET auxiliary=? WHERE id=?',(aux,vid))
        aux_note=f'Canonical compound examples use {aux}. '
        if word in DUAL:aux_note+='Auxiliary can change with meaning or transitivity; movement without a direct object and transitive uses must be distinguished. '
        aux_note+='A reflexive construction uses être, even when the non-reflexive verb uses avoir.'
        agreement='With être, past participles normally agree with the subject. The canonical form uses a masculine subject; feminine and formal-vous variants are stored separately. With avoir, no subject agreement is applied; a preceding direct object can change agreement. Reflexive agreement depends on the function of the reflexive pronoun.'
        usage=USAGE.get(word,'Use the complement and preposition appropriate to the intended sense. Finite reference forms do not include a subject pronoun. See the contextual usage example and sentence patterns.')
        conn.execute('INSERT INTO verb_reference VALUES (?,?,?,?,?,?,?)',(vid,source['ipa'],int(source['impersonal']),aux_note,agreement,usage,SOURCE))
        for key,forms in source['participles'].items():
            for form,ipa in forms:conn.execute('INSERT INTO verb_participles VALUES (?,?,?,?,?)',(vid,'present' if key=='present' else 'past','none' if key=='present' else key,form,VERB_IPA.get((word,form),ipa)))
        for mood,tense,person,variants in source['finite']:
            form,ipa=variants[0]
            ipa=VERB_IPA.get((word,form),ipa)
            conn.execute('INSERT INTO conjugations VALUES (?,?,?,?,?)',(vid,mood,tense,person,form))
            conn.execute('INSERT INTO conjugation_pronunciations VALUES (?,?,?,?,?,?,?,?)',(vid,mood,tense,person,ipa,dump([]),'dictionary' if ipa else 'not_supplied','Citation IPA; apply connected-speech rules.'))
            for alt,alt_ipa in variants[1:]:
                conn.execute('INSERT INTO conjugation_variants VALUES (?,?,?,?,?,?,?)',(vid,mood,tense,person,alt,VERB_IPA.get((word,alt),alt_ipa),'Alternative spelling or form recorded by Lefff; choose according to register and construction.'))

    compound_tenses=[('indicative','passe_compose','indicative','present'),
        ('indicative','pluperfect','indicative','imperfect'),('indicative','future_perfect','indicative','future'),
        ('conditional','past','conditional','present'),('subjunctive','past','subjunctive','present'),
        ('indicative','past_anterior','indicative','simple_past')]
    for word,source in ref['verbs'].items():
        vid=ids[word];aux='être' if word in ETRE else 'avoir';aid=ids[aux]
        people=['il'] if source['impersonal'] else PERSONS
        for mood,tense,amood,atense in compound_tenses:
            for person in people:
                aperson='il/elle/on' if person=='il' else person
                acell=conn.execute('SELECT c.form,p.ipa FROM conjugations c JOIN conjugation_pronunciations p USING(verb_id,mood,tense,person) WHERE c.verb_id=? AND c.mood=? AND c.tense=? AND c.person=?',(aid,amood,atense,aperson)).fetchone()
                if not acell:continue
                plural=person in ('nous','vous','ils/elles')
                key='mp' if aux=='être' and plural else 'ms'
                pp=source['participles'][key][0]
                form=acell[0]+' '+pp[0]
                conn.execute('INSERT INTO conjugations VALUES (?,?,?,?,?)',(vid,mood,tense,person,form))
                parts=[{'text':acell[0],'ipa':acell[1]},{'text':pp[0],'ipa':pp[1]}]
                conn.execute('INSERT INTO conjugation_pronunciations VALUES (?,?,?,?,?,?,?,?)',(vid,mood,tense,person,None,dump(parts),'word_parts','Separate-word IPA; connected speech varies.'))
                if aux=='être':
                    keys=['fp' if plural else 'fs']
                    if person=='vous':keys+=['ms','fs']
                    for gender_key in keys:
                        for ppf,ppi in source['participles'][gender_key]:
                            variant=acell[0]+' '+ppf
                            if variant!=form:conn.execute('INSERT OR IGNORE INTO conjugation_variants VALUES (?,?,?,?,?,?,?)',(vid,mood,tense,person,variant,None,'Subject agreement variant; select gender and singular/formal-vous or plural context.'))
        groups=defaultdict(list)
        for mood,tense,person in conn.execute('SELECT mood,tense,person FROM conjugations WHERE verb_id=?',(vid,)):groups[(mood,tense)].append(person)
        for (mood,tense),available in groups.items():
            expected=['il'] if source['impersonal'] else ['tu','nous','vous'] if mood=='imperative' else PERSONS
            status='complete' if set(expected)==set(available) else 'source_gap'
            conn.execute('INSERT INTO conjugation_coverage VALUES (?,?,?,?,?,?)',(vid,mood,tense,dump(expected),dump(sorted(available)),status))
    for lid,word,pos,_ in conn.execute('SELECT id,french,part_of_speech,gender FROM lexemes').fetchall():
        if pos=='verb':conn.execute("UPDATE conversation_words SET verb_id=?,conjugation_status='available' WHERE lexeme_id=?",(ids[word],lid))
    with (ROOT/'completion_usage.tsv').open(encoding='utf-8') as f:
        rows=list(csv.DictReader(f,delimiter='\t'))
    assert len(rows)==1000
    for row in rows:
        conn.execute('UPDATE conversation_words SET example_fr=?,example_en=?,example_status=?,example_source=? WHERE french=?',(row['example_fr'],row['example_en'],row['example_status'],row['example_source'],row['french']))
    for word,(pos,meaning,fr,en) in SENSE_FIXES.items():
        conn.execute('UPDATE lexemes SET english=? WHERE french=?',(meaning,word))
        conn.execute("UPDATE conversation_words SET meaning_en=?,example_fr=?,example_en=?,example_status='authored_unreviewed',example_source='Original project sense correction' WHERE french=?",(meaning,fr,en,word))
        conn.execute("UPDATE flashcards SET back=? WHERE lexeme_id=(SELECT id FROM lexemes WHERE french=?) AND direction='fr_en'",(meaning,word))
        conn.execute("UPDATE flashcards SET front=? WHERE lexeme_id=(SELECT id FROM lexemes WHERE french=?) AND direction='en_fr'",(meaning,word))
    china_id=conn.execute("SELECT id FROM lexemes WHERE french='chine'").fetchone()
    if china_id:
        conn.execute("UPDATE lexemes SET french='Chine' WHERE id=?",china_id)
        conn.execute("UPDATE conversation_words SET french='Chine' WHERE lexeme_id=?",china_id)
        conn.execute("UPDATE flashcards SET front='Chine' WHERE lexeme_id=? AND direction='fr_en'",china_id)
        conn.execute("UPDATE flashcards SET back='Chine' WHERE lexeme_id=? AND direction='en_fr'",china_id)
    sources=[(SOURCE,'Lefff 3.4 morphology','LGPL-LR; extracted finite forms and noun/adjective inflections. Source hashes and extraction script are supplied.'),
             ('https://github.com/open-dict-data/ipa-dict','IPA dictionary','Citation pronunciations; connected speech and homographs require context.'),
             ('https://tatoeba.org','Tatoeba examples','CC BY 2.0 France; corpus-derived examples remain unreviewed.')]
    conn.executemany('INSERT OR IGNORE INTO content_sources(source_url,title,usage_note) VALUES (?,?,?)',sources)
    apply_pronominal_content(conn)
