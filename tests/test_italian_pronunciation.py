from __future__ import annotations

import re
import unittest

from lang_practice.languages.italian.data import PRESENT_TENSE, SENTENCES, VOCABULARY
from lang_practice.languages.italian.pronunciation import explain_pronunciation, to_ipa, to_phonetic


class ItalianPronunciationTests(unittest.TestCase):
    def test_corrected_guide_examples(self) -> None:
        expected = {
            "ciao": ("/ˈtʃao/", "CHOW"),
            "mela": ("/ˈme.la/", "MÉ-lah"),
            "vespa": ("/ˈvɛs.pa/", "VÈS-pah"),
            "pesce": ("/ˈpeʃ.ʃe/", "PÉSH-sheh"),
            "sciare": ("/ʃiˈa.re/", "shee-AH-ré"),
            "gli": ("/ʎi/", "lyee"),
            "famiglia": ("/faˈmiʎ.ʎa/", "fah-MEE-lyah"),
            "gnocchi": ("/ˈɲɔk.ki/", "NYÒK-kee"),
            "stazione": ("/statˈtsjo.ne/", "staht-TSYÓ-neh"),
            "spiaggia": ("/ˈspjad.dʒa/", "SPYAH-jah"),
            "perché": ("/per.ˈke/", "pehr-KÉ"),
            "caffè": ("/kafˈfɛ/", "kahf-FÈ"),
        }
        for word, (ipa, helper) in expected.items():
            with self.subTest(word=word):
                self.assertEqual(to_ipa(word), ipa)
                self.assertEqual(to_phonetic(word), helper)

    def test_every_bundled_italian_item_renders(self) -> None:
        texts = [item.french for item in VOCABULARY]
        texts.extend(pattern.infinitive for pattern in PRESENT_TENSE)
        texts.extend(sentence.french for sentence in SENTENCES)
        for text in texts:
            with self.subTest(text=text):
                self.assertRegex(to_ipa(text), r"^/.+/$")
                self.assertTrue(to_phonetic(text).strip())

    def test_sentence_keeps_apostrophes_and_language_specific_values(self) -> None:
        sentence = "Dov'è la stazione?"
        self.assertEqual(to_ipa(sentence), "/doˈvɛ la statˈtsjo.ne/")
        self.assertEqual(to_phonetic(sentence), "dó-VÈ lah staht-TSYÓ-neh")

    def test_unknown_word_is_explicitly_approximate(self) -> None:
        explanation = explain_pronunciation("zebrone")
        self.assertIn("fallback", explanation.casefold())
        self.assertTrue(re.search(r"s/z|dictionary", explanation, re.IGNORECASE))


if __name__ == "__main__":
    unittest.main()
