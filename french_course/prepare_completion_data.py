#!/usr/bin/env python3
"""Extract a reproducible Lefff/IPA subset; source dumps stay outside the repo.

Usage: python french_course/prepare_completion_data.py --source-dir /tmp/french-content-audit
Run against the existing course database. The offline build reads the saved JSON.
Lefff-derived records are LGPL-LR; see licenses/Lefff-LGPL-LR.txt.
"""
import argparse
import collections
import hashlib
import json
import re
import sqlite3
import unicodedata
from pathlib import Path
from reflexive_content import ROUTINES

ROOT = Path(__file__).resolve().parent
TAG_POS = {'nc':'noun', 'np':'proper_noun', 'adj':'adjective', 'adv':'adverb',
           'advneg':'adverb', 'prep':'preposition', 'coo':'conjunction', 'csu':'conjunction',
           'det':'determiner', 'pro':'pronoun', 'prel':'pronoun', 'pri':'pronoun',
           'cln':'pronoun', 'cla':'pronoun', 'cld':'pronoun', 'clr':'pronoun',
           'clar':'pronoun', 'cldr':'pronoun', 'clg':'pronoun', 'cll':'pronoun',
           'ce':'pronoun', 'caimp':'pronoun', 'ilimp':'pronoun', 'clneg':'adverb',
           'pres':'interjection'}
NUMBERS = set('deux trois quatre cinq six sept huit neuf dix douze quinze vingt trente quarante cinquante cent mille million premier'.split())
PRIMARY = {
    **dict.fromkeys('de par entre vers jusque dès malgré selon parmi'.split(), 'preposition'),
    **dict.fromkeys('son ton notre votre quelque quel chaque certain tel aucun toute tout'.split(), 'determiner'),
    **dict.fromkeys('se me on lui y moi te toi celui rien lequel chacun ça cela ceci quelqu’un l’un l’une d’autres auquel dont'.split(), 'pronoun'),
    **dict.fromkeys('et mais ou car ni puisque lorsque soit'.split(), 'conjunction'),
    **dict.fromkeys('en ce leur'.split(), 'pronoun'),
    **dict.fromkeys('ah oh eh salut'.split(), 'interjection'),
    **dict.fromkeys('voilà voici'.split(), 'expression'),
    **dict.fromkeys('puis fort ensemble également aussi bien plus pas ne'.split(), 'adverb'),
    **dict.fromkeys('mort fin or est tour personne froid gauche bête'.split(), 'noun'),
    'pouvoir':'verb', 'du':'article', 'au':'preposition', 'cœur':'noun', 'œil':'noun',
    'œuvre':'noun', 'ci':'adverb', 'afin de':'preposition', 'tandis que':'conjunction',
}
TENSES = {'P':('indicative','present'), 'I':('indicative','imperfect'),
          'F':('indicative','future'), 'C':('conditional','present'),
          'S':('subjunctive','present'), 'J':('indicative','simple_past'),
          'T':('subjunctive','imperfect'), 'Y':('imperative','present')}
PERSONS = ['je','tu','il/elle/on','nous','vous','ils/elles']

def norm(s):
    return unicodedata.normalize('NFC',s).replace('’',"'").replace('œ','oe').replace('æ','ae').lower()

def prepare(source_dir):
    c=sqlite3.connect(ROOT/'french_course.sqlite'); c.row_factory=sqlite3.Row
    words=[dict(r) for r in c.execute('SELECT * FROM lexemes ORDER BY id')]
    # The importer can run against a completed DB; the base seed uses lowercase chine.
    for word in words:
        if word['french']=='Chine':word['french']='chine'
    surface=collections.defaultdict(list); lemma=collections.defaultdict(list)
    for line in (source_dir/'lefff.mlex').read_text().splitlines():
        p=line.split('\t')
        if len(p)<4: continue
        form,tag,base,features=p[:4]
        if not re.fullmatch(r"[^\W\d_]+(?:[- '’][^\W\d_]+)*",form,re.UNICODE): continue
        surface[norm(form)].append((form,tag,base,features))
        lemma[norm(base)].append((form,tag,base,features))
    ipa={}
    for line in (source_dir/'ipa-fr.txt').read_text().splitlines():
        p=line.split('\t')
        if len(p)==2: ipa[norm(p[0])]=p[1]
    lexical={}; verb_words=set(r['infinitive'] for r in c.execute('SELECT infinitive FROM verbs'))|set(ROUTINES)
    for word in words:
        w=word['french']; entries=surface[norm(w)]
        poss=sorted({TAG_POS[t] for _,t,_,_ in entries if t in TAG_POS})
        if any(t=='v' and norm(base)==norm(w) and 'W' in f for _,t,base,f in entries):
            poss.append('verb')
        primary=word['part_of_speech']
        if primary=='unclassified':
            if w in PRIMARY: primary=PRIMARY[w]
            elif w in NUMBERS: primary='numeral'
            elif 'adjective' in poss: primary='adjective'
            elif 'noun' in poss: primary='noun'
            elif poss: primary=poss[0]
            else: raise ValueError(('Unclassified',w))
        if primary=='verb': verb_words.add(w)
        poss=sorted(set(poss+[primary]))
        wanted_tag={'noun':'nc','adjective':'adj'}.get(primary)
        roots=sorted({base for _,tag,base,_ in entries if tag==wanted_tag})
        forms=[]
        for base in roots:
            for f,t,b,features in lemma[norm(base)]:
                if t!=wanted_tag:continue
                if 'œ' in w: f=f.replace('oe','œ')
                row=[f,features,ipa.get(norm(f))]
                if row not in forms: forms.append(row)
        genders=sorted({g for _,t,_,feats in entries if t=='nc' for g in 'mf' if g in feats})
        lexical[w]={'primary_pos':primary,'parts_of_speech':poss,'lemmas':roots or [w],
                    'genders':genders,'forms':sorted(forms), 'source_tags':sorted({t for _,t,_,_ in entries})}
    verbs={}
    for w in sorted(verb_words):
        cells=collections.defaultdict(set); participles=collections.defaultdict(set)
        for form,tag,base,code in lemma[norm(w)]:
            if tag!='v' or (w=='être' and form=='st'):continue
            # Lefff contains orthographic alternatives; retain them separately.
            if not re.fullmatch(r'[^\W\d_]+',form,re.UNICODE):continue
            if 'K' in code:
                for gender in ('m','f'):
                    for number in ('s','p'):
                        if (gender in code or not any(g in code for g in 'mf')) and (number in code or not any(n in code for n in 'sp')):
                            participles[gender+number].add(form)
            if 'G' in code:participles['present'].add(form)
            for letter,(mood,tense) in TENSES.items():
                if letter not in code:continue
                for n in 'sp':
                    for person in '123':
                        if n in code and person in code:
                            index=int(person)-1+(3 if n=='p' else 0)
                            if mood=='imperative' and index not in (1,3,4):continue
                            label='il' if w=='falloir' else PERSONS[index]
                            cells[(mood,tense,label)].add(form)
        if not cells: raise ValueError(('No verb data',w))
        finite=[]
        for (mood,tense,person),variants in sorted(cells.items()):
            variants=sorted(variants,key=lambda f:(not bool(ipa.get(norm(f))), f))
            if w=='pouvoir' and mood=='indicative' and tense=='present' and person=='je':
                variants=sorted(variants,key=lambda f:f!='peux')
            finite.append([mood,tense,person,[[v,ipa.get(norm(v))] for v in variants]])
        verbs[w]={'ipa':ipa.get(norm(w)), 'finite':finite,
                  'participles':{k:[[f,ipa.get(norm(f))] for f in sorted(v)] for k,v in participles.items()},
                  'impersonal':w=='falloir'}
    output={'sources':{name:hashlib.sha256((source_dir/name).read_bytes()).hexdigest() for name in ['lefff.mlex','ipa-fr.txt']},
            'lexical':lexical, 'verbs':verbs}
    path=ROOT/'completion_reference.json'
    path.write_text(json.dumps(output,ensure_ascii=False,separators=(',',':'))+'\n')
    print('Saved',path,len(lexical),'words',len(verbs),'verbs',sum(len(v['finite']) for v in verbs.values()),'finite cells')
    print('IPA missing',sum(not v[1] for r in verbs.values() for cell in r['finite'] for v in cell[3]))
    print('Non-six present',[(w,[f[2] for f in v['finite'] if f[:2]==['indicative','present']]) for w,v in verbs.items() if len([f for f in v['finite'] if f[:2]==['indicative','present']])!=6])

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--source-dir',type=Path,required=True)
    prepare(parser.parse_args().source_dir)
