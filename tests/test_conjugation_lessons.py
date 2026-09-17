import unittest

from lang_practice.languages.french import MODULE as FRENCH
from lang_practice.languages.italian import MODULE as ITALIAN


class ConjugationLessonTests(unittest.TestCase):
    def _pattern(self, module, infinitive):
        return next(pattern for pattern in module.present_tense if pattern.infinitive == infinitive)

    def test_italian_dovere_explains_each_stem_group(self):
        lesson = ITALIAN.explain_conjugation(self._pattern(ITALIAN, "dovere"))

        self.assertIn("dev-", lesson)
        self.assertIn("dobbiamo", lesson)
        self.assertIn("dovete", lesson)
        self.assertIn("devono", lesson)

    def test_italian_regular_are_explains_removal_and_endings(self):
        lesson = ITALIAN.explain_conjugation(self._pattern(ITALIAN, "parlare"))

        self.assertIn("Remove -are", lesson)
        self.assertIn("-iamo", lesson)

    def test_italian_lessons_teach_a_reconstruction_method(self):
        for infinitive in ("parlare", "capire", "potere"):
            with self.subTest(infinitive=infinitive):
                lesson = ITALIAN.explain_conjugation(self._pattern(ITALIAN, infinitive))
                self.assertIn("BIG IDEA", lesson)
                self.assertIn("BUILD THE FORM", lesson)
                self.assertIn("PATTERN TO NOTICE", lesson)
                self.assertIn("TRY THIS METHOD", lesson)

    def test_italian_irregular_lesson_groups_related_subjects(self):
        lesson = ITALIAN.explain_conjugation(self._pattern(ITALIAN, "potere"))

        self.assertIn("3-2-1", lesson)
        self.assertIn("io, noi, and loro", lesson)
        self.assertIn("tu and lui/lei", lesson)

    def test_french_aller_explains_stem_groups(self):
        lesson = FRENCH.explain_conjugation(self._pattern(FRENCH, "aller"))

        self.assertIn("va-", lesson)
        self.assertIn("all-", lesson)
        self.assertIn("vont", lesson)

    def test_every_current_pattern_has_a_substantive_lesson(self):
        for module in (FRENCH, ITALIAN):
            for pattern in module.present_tense:
                with self.subTest(language=module.key, infinitive=pattern.infinitive):
                    lesson = module.explain_conjugation(pattern)
                    self.assertGreater(len(lesson), 80)


if __name__ == "__main__":
    unittest.main()
