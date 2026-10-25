"""Common pronominal constructions, using the source-backed base paradigms."""
import json
import re

ROUTINES={
    'lever':('se lever','get up','A daily routine. Contrast lever quelque chose, to lift something.'),
    'coucher':('se coucher','go to bed','Contrast coucher un enfant, to put a child to bed.'),
    'réveiller':('se réveiller','wake up','Contrast réveiller quelqu’un, to wake someone else.'),
    'laver':('se laver','wash oneself','The participle agrees in elle s’est lavée. It does not agree with the subject in elle s’est lavé les mains, because les mains is the following direct object.'),
    'habiller':('s’habiller','get dressed','H is mute here, so use je m’habille.'),
    'préparer':('se préparer','get ready','Se préparer à + noun/infinitive, or se préparer pour an event.'),
    'arrêter':('s’arrêter','stop','Contrast arrêter quelque chose, to stop something.'),
    'reposer':('se reposer','rest','Contrast reposer un objet, to put an object down again.'),
    'appeler':('s’appeler','be called; call oneself','Use je m’appelle to give a name.'),
    'souvenir':('se souvenir','remember','Se souvenir de + noun/infinitive. Souvenir without se is also the noun memory or souvenir.'),
    'asseoir':('s’asseoir','sit down','Assieds-toi and assois-toi belong to accepted alternative paradigms; this table follows the base canonical choice.'),
    'concentrer':('se concentrer','concentrate','Se concentrer sur quelque chose.'),
    'promener':('se promener','go for a walk','Contrast promener un chien, to walk a dog.'),
    'dépêcher':('se dépêcher','hurry','Se dépêcher de + infinitive: Dépêche-toi de partir.'),
}
PRONOUNS={'je':'me','tu':'te','il/elle/on':'se','nous':'nous','vous':'vous','ils/elles':'se'}

def prefix(person,form):
    pronoun=PRONOUNS[person]
    if pronoun in ('me','te','se') and re.match(r'^[aeiouyàâéèêëîïôùûüœh]',form,re.I):
        return pronoun[0]+'’'+form
    return pronoun+' '+form

def apply(conn):
    for rid,(base,(lemma,english,note)) in enumerate(ROUTINES.items(),1):
        vid=conn.execute('SELECT id FROM verbs WHERE infinitive=?',(base,)).fetchone()[0]
        conn.execute('INSERT INTO pronominal_verbs VALUES (?,?,?,?,?)',(rid,lemma,vid,english,note))
        cells=conn.execute("SELECT mood,tense,person,form FROM conjugations WHERE verb_id=? AND ((mood IN ('indicative','conditional','subjunctive') AND tense IN ('present','imperfect','future')) OR mood='imperative')",(vid,)).fetchall()
        for mood,tense,person,form in cells:
            if mood=='imperative':
                reflexive={'tu':'toi','nous':'nous','vous':'vous'}[person]
                out=form+'-'+reflexive
            else:out=prefix(person,form)
            conn.execute('INSERT INTO pronominal_conjugations VALUES (?,?,?,?,?,?,?)',(rid,mood,tense,person,out,'[]','Declarative pronouns precede the verb; affirmative-imperative pronouns follow it. These forms have no subject pronoun attached.'))
        for mood,tense,aux_mood,aux_tense in [('indicative','passe_compose','indicative','present'),('indicative','pluperfect','indicative','imperfect'),('conditional','past','conditional','present')]:
            etre=conn.execute("SELECT c.person,c.form FROM conjugations c JOIN verbs v ON v.id=c.verb_id WHERE v.infinitive='être' AND c.mood=? AND c.tense=?",(aux_mood,aux_tense)).fetchall()
            for person,aux_form in etre:
                key='mp' if person in ('nous','vous','ils/elles') else 'ms'
                pp=conn.execute("SELECT form FROM verb_participles WHERE verb_id=? AND kind='past' AND agreement=? ORDER BY form LIMIT 1",(vid,key)).fetchone()[0]
                out=prefix(person,aux_form)+' '+pp
                other_keys=['fp' if key=='mp' else 'fs']+(['ms','fs'] if person=='vous' else [])
                variants=[]
                for k in other_keys:
                    for (alt,) in conn.execute("SELECT form FROM verb_participles WHERE verb_id=? AND kind='past' AND agreement=? ORDER BY form",(vid,k)):
                        candidate=prefix(person,aux_form)+' '+alt
                        if candidate!=out and candidate not in variants:variants.append(candidate)
                conn.execute('INSERT INTO pronominal_conjugations VALUES (?,?,?,?,?,?,?)',(rid,mood,tense,person,out,json.dumps(variants,ensure_ascii=False),'Canonical forms use a masculine subject in a basic reflexive construction. Select agreement for the actual construction; a following direct object or an indirect reflexive pronoun changes the rule.'))
