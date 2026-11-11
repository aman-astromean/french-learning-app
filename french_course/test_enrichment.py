"""Structural and evidence regression checks; not independent linguistic review."""
import json
import sqlite3
import unittest
from pathlib import Path

class EnrichmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db=sqlite3.connect(Path(__file__).with_name('french_course.sqlite'))
        cls.db.row_factory=sqlite3.Row

    @classmethod
    def tearDownClass(cls): cls.db.close()

    def test_level_coverage(self):
        self.assertEqual([r[0] for r in self.db.execute('SELECT unit_id FROM skill_packs ORDER BY unit_id')],list(range(3,61)))
        for table,count in [('skill_resources',116),('comprehension_questions',290),('comprehension_options',870),('dialogue_turns',348),('production_tasks',116),('production_rubrics',464),('skill_expressions',174),('skill_schedule',290)]:
            self.assertEqual(self.db.execute('SELECT COUNT(*) FROM '+table).fetchone()[0],count,table)

    def test_progressive_text_and_dialogue(self):
        minimum={'A1':50,'A2':75,'B1':100,'B2':125,'C1':125,'C2':125}
        for r in self.db.execute('SELECT r.*,u.level_code FROM skill_resources r JOIN units u ON u.id=r.unit_id'):
            if r['kind']=='reading': self.assertGreaterEqual(len(r['text_fr'].split()),minimum[r['level_code']],r['title'])
            else: self.assertEqual(self.db.execute('SELECT COUNT(*) FROM dialogue_turns WHERE resource_id=?',(r['id'],)).fetchone()[0],6)

    def test_questions_have_evidence_and_balanced_options(self):
        for q in self.db.execute('SELECT q.*,r.text_fr FROM comprehension_questions q JOIN skill_resources r ON r.id=q.resource_id'):
            self.assertIn(q['evidence_fr'].casefold(),q['text_fr'].casefold())
            options=self.db.execute('SELECT * FROM comprehension_options WHERE question_id=?',(q['id'],)).fetchall()
            self.assertEqual(len({r['text_fr'] for r in options}),3)
            self.assertEqual(sum(r['correct'] for r in options),1)
        self.assertEqual({r[0] for r in self.db.execute('SELECT DISTINCT position FROM comprehension_options WHERE correct=1')},{0,1,2})

    def test_schedule_preserves_a0_and_required_time(self):
        for r in self.db.execute('SELECT s.*,l.day_number,l.day_in_unit,l.unit_id AS lesson_unit FROM skill_schedule s JOIN lessons l ON l.id=s.lesson_id'):
            self.assertGreater(r['day_number'],14)
            self.assertEqual(r['unit_id'],r['lesson_unit'])
            self.assertEqual(r['day_in_unit'],{'reading':2,'dialogue':3,'writing':5,'speaking':6,'review':7}[r['activity']])
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM lessons').fetchone()[0],420)

    def test_honest_media_and_assessment_status(self):
        self.assertEqual({r[0] for r in self.db.execute('SELECT audio_status FROM skill_resources')},{'not_recorded'})
        self.assertEqual({r[0] for r in self.db.execute('SELECT auto_gradable FROM production_tasks')},{0})
        self.assertEqual({r[0] for r in self.db.execute('SELECT review_status FROM skill_packs')},{'editorial_review_pending'})
        self.assertEqual(self.db.execute('SELECT COUNT(DISTINCT unit_id) FROM skill_pronunciation').fetchone()[0],58)
        self.assertFalse(self.db.execute('PRAGMA foreign_key_check').fetchall())

    def test_no_private_reference_identifiers(self):
        for p in (Path(__file__).parent/'enrichment').glob('*.py'):
            self.assertNotIn('drive.google.com',p.read_text())
            self.assertNotIn('1oRlW9LhWR',p.read_text())

    def test_export_matches_database(self):
        path=Path(__file__).parents[1]/'web/data/enrichment_reference.json'
        if not path.exists(): self.skipTest('Run web/export_course.py for export checks')
        data=json.loads(path.read_text())
        self.assertEqual(len(data['packs']),58)
        self.assertEqual(sum(len(r['questions']) for p in data['packs'] for r in p['resources']),290)
        for p in data['packs']:
            level=json.loads((path.parent/(p['level_code'].lower()+'.json')).read_text())
            for s in p['schedule']:
                self.assertEqual(level[str(s['lesson_id'])]['enrichment']['schedule']['activity'],s['activity'])
