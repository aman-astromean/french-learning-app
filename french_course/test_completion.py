"""Regression checks for linguistic edge cases, not a claim of educator review.

Run after build.py: python -m unittest discover -s french_course -p 'test_*.py'
"""
import json
import sqlite3
import unittest
from pathlib import Path

class CompletedCourseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db=sqlite3.connect(Path(__file__).with_name('french_course.sqlite'))

    @classmethod
    def tearDownClass(cls):cls.db.close()

    def form(self,verb,person,mood='indicative',tense='present'):
        r=self.db.execute('SELECT c.form FROM conjugations c JOIN verbs v ON v.id=c.verb_id WHERE v.infinitive=? AND c.person=? AND c.mood=? AND c.tense=?',(verb,person,mood,tense)).fetchone()
        return r[0] if r else None

    def test_bank_completion(self):
        self.assertEqual(self.db.execute('SELECT COUNT(DISTINCT french) FROM conversation_words').fetchone()[0],3000)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM conversation_words WHERE conjugation_status='pending_review' OR example_status='draft'").fetchone()[0],0)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM lexemes WHERE part_of_speech='unclassified'").fetchone()[0],0)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM conversation_words WHERE example_fr LIKE 'Comment emploie-t-on%' OR example_fr LIKE 'Comment utilise-t-on%'").fetchone()[0],0)

    def test_impersonal_falloir(self):
        self.assertEqual(self.form('falloir','il'),'faut')
        self.assertEqual(self.form('falloir','il',tense='passe_compose'),'a fallu')
        self.assertIsNone(self.form('falloir','je'))
        self.assertIsNone(self.form('falloir','tu',mood='imperative'))

    def test_spelling_changes(self):
        for v,p,expected in [('acheter','je','achète'),('acheter','nous','achetons'),('manger','nous','mangeons'),('commencer','nous','commençons'),('répéter','je','répète'),('appuyer','je','appuie')]:
            with self.subTest(v=v,p=p):self.assertEqual(self.form(v,p),expected)
        self.assertEqual(self.form('commencer','nous',tense='imperfect'),'commencions')
        self.assertEqual(self.form('reprendre','nous'),'reprenons')
        self.assertEqual(self.form('reprendre','ils/elles'),'reprennent')

    def test_normalized_tenses(self):
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM conjugations WHERE mood='conditional' AND tense='conditional'").fetchone()[0],0)
        self.assertEqual(self.form('être','je',mood='conditional'),'serais')
        self.assertEqual(self.form('avoir','nous',mood='subjunctive'),'ayons')
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM conjugation_coverage WHERE status!='complete'").fetchone()[0],0)

    def test_compound_auxiliary_and_agreement(self):
        self.assertEqual(self.form('être','je',tense='passe_compose'),'ai été')
        self.assertEqual(self.form('aller','nous',tense='passe_compose'),'sommes allés')
        self.assertEqual(self.form('arriver','je',tense='pluperfect'),'étais arrivé')
        self.assertEqual(self.form('manger','nous',tense='passe_compose'),'avons mangé')
        variants={r[0] for r in self.db.execute("SELECT c.form FROM conjugation_variants c JOIN verbs v ON v.id=c.verb_id WHERE v.infinitive='aller' AND mood='indicative' AND tense='passe_compose' AND person='vous'")}
        self.assertTrue({'êtes allé','êtes allée','êtes allées'}.issubset(variants))

    def test_morphology_and_sense(self):
        self.assertTrue(self.db.execute("SELECT 1 FROM lexical_inflections i JOIN lexemes l ON l.id=i.lexeme_id WHERE l.french='cheval' AND i.form='chevaux'").fetchone())
        self.assertEqual(self.db.execute("SELECT gender FROM lexemes WHERE french='mémoire'").fetchone()[0],'f')
        self.assertEqual(self.db.execute("SELECT gender FROM lexemes WHERE french='poêle'").fetchone()[0],'f')
        self.assertEqual(self.db.execute("SELECT part_of_speech FROM lexemes WHERE french='pouvoir'").fetchone()[0],'verb')

    def test_pronominal_routines(self):
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM pronominal_verbs').fetchone()[0],14)
        for lemma,mood,tense,person,expected in [('se lever','indicative','present','je','me lève'),('s’habiller','indicative','present','je','m’habille'),('se souvenir','indicative','passe_compose','je','me suis souvenu'),('se dépêcher','imperative','present','tu','dépêche-toi')]:
            actual=self.db.execute('SELECT c.form FROM pronominal_conjugations c JOIN pronominal_verbs v ON v.id=c.pronominal_verb_id WHERE v.lemma=? AND c.mood=? AND c.tense=? AND c.person=?',(lemma,mood,tense,person)).fetchone()[0]
            self.assertEqual(actual,expected)

    def test_pronunciation_provenance(self):
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM lexemes WHERE ipa IS NULL OR trim(ipa)=''").fetchone()[0],0)
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM vocabulary_pronunciation').fetchone()[0],3000)
        ipa=self.db.execute("SELECT p.ipa FROM conjugation_pronunciations p JOIN verbs v ON v.id=p.verb_id WHERE v.infinitive='être' AND p.person='il/elle/on' AND p.mood='indicative' AND p.tense='present'").fetchone()[0]
        self.assertEqual(ipa,'/ɛ/')
        for (parts,) in self.db.execute("SELECT word_parts_json FROM conjugation_pronunciations WHERE status='word_parts'"):
            self.assertEqual(len(json.loads(parts)),2)

    def test_sentence_construction(self):
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM sentence_patterns').fetchone()[0],80)
        for components,expected in self.db.execute('SELECT components_json,example_fr FROM sentence_patterns'):
            self.assertEqual(' '.join(p['text'] for p in json.loads(components)),expected)
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM sentence_tasks').fetchone()[0],160)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM sentence_tasks WHERE kind='translation' AND auto_gradable=1").fetchone()[0],0)
        self.assertEqual(self.db.execute('SELECT COUNT(DISTINCT lexeme_id) FROM sentence_pattern_words').fetchone()[0],3000)

    def test_integrity(self):
        self.assertEqual(self.db.execute('PRAGMA integrity_check').fetchone()[0],'ok')
        self.assertEqual(self.db.execute('PRAGMA foreign_key_check').fetchall(),[])
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM learners').fetchone()[0],0)

if __name__=='__main__':unittest.main()
