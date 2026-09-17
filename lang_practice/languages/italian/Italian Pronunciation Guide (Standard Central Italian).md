# Italian Pronunciation Guide

## Standard Central Italian and learner-facing phonetic helpers

This guide describes a broadly accepted educated pronunciation of Standard
Italian, with Central Italian as the reference point. It is intended for
language learners and for software that displays IPA and an approximate
English-oriented pronunciation helper.

Italian spelling is comparatively regular, but it does **not** determine every
detail of pronunciation. In particular, ordinary spelling often leaves these
features unspecified:

- the position of stress when it is not written;
- whether a stressed `e` is /e/ or /ɛ/;
- whether a stressed `o` is /o/ or /ɔ/;
- whether a single `s` is /s/ or /z/ in lexically variable positions;
- whether `z` is /ts/ or /dz/;
- whether adjacent vowels form one syllable or a hiatus in some words.

For those features, a pronunciation dictionary or a curated lexical entry is
more reliable than a spelling-only algorithm. Regional variation is normal,
especially for open and closed `e`/`o`, intervocalic `s`, `z`, and connected
speech. A learner should aim for consistency and intelligibility rather than
treat every regional difference as an error.

## Notation

- `/slashes/` contain broad phonemic IPA: the meaningful sound pattern.
- `[brackets]` contain a narrower phonetic realization when needed.
- `ˈ` appears immediately before the stressed syllable.
- `ː` marks a long consonant or, in narrow transcription, predictable vowel
  length.
- Learner respellings are approximations. IPA and recorded native speech remain
  authoritative.

This guide normally omits predictable vowel length from broad IPA. In careful
Standard Italian, a stressed vowel in a non-final open syllable is commonly
longer, but vowel length is not independently contrastive. For example, *cane*
may be narrowly transcribed `[ˈkaːne]`, while broad `/ˈkane/` is sufficient for
the learner-facing system.

## Vowels

Standard Italian has seven stressed vowel phonemes.

| Spelling | IPA | Learner cue | Example |
|---|---:|---|---|
| `a` | /a/ | `ah`, as in *father* | *cane* /ˈkane/ |
| `e`, sometimes `é` | /e/ | a pure closed `é`; begin English *say* but do not add a `y` glide | *mela* /ˈmela/ |
| `e`, sometimes `è` | /ɛ/ | `eh`, as in *bed* | *bello* /ˈbɛllo/ |
| `i` | /i/ | `ee`, as in *see* | *vino* /ˈvino/ |
| `o`, sometimes `ó` | /o/ | a pure closed `ó`; no final `w` glide | *dove* /ˈdove/ |
| `o`, sometimes `ò` | /ɔ/ | open `aw` | *cosa* /ˈkɔza/ |
| `u` | /u/ | `oo`, as in *food* | *luna* /ˈluna/ |

Unstressed `e` and `o` are normally realized as the closed vowels [e] and [o]
in the reference pronunciation. All vowels should remain clear; do not reduce
unstressed vowels to the English schwa merely because they are unstressed.

### Written accents

Italian normally writes an accent on a vowel-final word stressed on its final
syllable: *città*, *perché*, *caffè*, *così*, *però*, *virtù*. It also uses
accents to distinguish certain monosyllables, such as *e* "and" versus *è*
"is" and *si* versus *sì*.

For `e` and `o`, an acute accent indicates a closed vowel (`é` /e/, `ó` /o/),
while a grave accent indicates an open vowel (`è` /ɛ/, `ò` /ɔ/). Ordinary
internal spelling usually omits these quality marks, so the correct vowel may
need a dictionary lookup.

## Adjacent vowels, glides, and hiatus

The letters `i` and `u` can represent the vowels /i, u/ or the glides /j, w/.
The spelling alone does not always settle the choice.

- *piano* /ˈpjano/ contains /j/ and begins with one syllable /pja/.
- *uomo* /ˈwɔmo/ begins with /w/.
- *mai* /mai/ and *poi* /pɔi/ contain falling vowel sequences.
- *paese* /paˈeze/ and *idea* /iˈdɛa/ contain hiatus: both adjacent vowels are
  syllabic.
- *io* /ˈio/ has two vowel nuclei; it is not generally `/jo/`.
- *sciare* /ʃiˈare/ retains a pronounced /i/ and has hiatus.

Do not turn every written `i` or `u` next to another vowel into a glide. A
spelling-only helper should use curated exceptions or mark uncertain outputs as
approximate.

## Core consonants

`b d f m n p t v` are broadly similar to their English counterparts. Italian
voiceless stops /p t k/ are normally less aspirated than English initial stops.
Italian `l` is generally clear rather than the dark English `l` of *ball*.

### C and G

- `c` is /k/ before `a o u`, before a consonant, and in `ch` before `e i`:
  *cane* /ˈkane/, *cosa* /ˈkɔza/, *chi* /ki/.
- `c` is /tʃ/ before `e i`: *cena* /ˈtʃena/, *cibo* /ˈtʃibo/.
- `g` is /ɡ/ before `a o u`, before a consonant, and in `gh` before `e i`:
  *gatto* /ˈɡatto/, *spaghetti* /spaˈɡetti/.
- `g` is /dʒ/ before `e i`: *gelato* /dʒeˈlato/, *giro* /ˈdʒiro/.

In sequences such as `cia`, `cio`, `giu`, and `gia`, the `i` is often a
diacritic that selects the soft consonant and is not a separate sound:
*ciao* /ˈtʃao/, *gioco* /ˈdʒɔko/. It is pronounced when lexical stress or the
word's structure requires it, as in *farmacia* /farmaˈtʃia/. Curated lexical
data must take precedence over a blanket "silent i" rule.

### SC

- `sc` is /ʃ/ before `e i`: *scena* /ˈʃena/, *pesce* /ˈpeʃʃe/.
- `sc` is /sk/ elsewhere: *scala* /ˈskala/, *scuola* /ˈskwɔla/.
- `sch` keeps /sk/ before `e i`: *schema* /ˈskema/, *schiena* /ˈskjɛna/.

In `scia`, `scio`, and `sciu`, `i` is commonly diacritic: *sciarpa*
/ˈʃarpa/, *sciocco* /ˈʃɔkko/. The verb *sciare* is an important lexical
exception: /ʃiˈare/.

### GN

`gn` normally represents the palatal nasal /ɲ/, made by raising the middle of
the tongue toward the hard palate. It resembles Spanish `ñ`, not a sequence
/ɡn/. Between vowels it is normally long in Standard Italian:

- *gnocchi* /ˈɲɔkki/
- *bagno* /ˈbaɲɲo/
- *montagna* /monˈtaɲɲa/

Some learned or borrowed words can preserve /ɡn/; consult a dictionary for such
exceptions.

### GLI

Before another vowel, `gli` usually represents the long palatal lateral /ʎʎ/;
the written `i` is then diacritic:

- *famiglia* /faˈmiʎʎa/
- *figlio* /ˈfiʎʎo/
- *biglietto* /biʎˈʎɛtto/

When `gli` ends a word or syllable and supplies the vowel, /i/ is pronounced:
the article *gli* is /ʎi/, and *figli* is /ˈfiʎʎi/. Some learned words retain a
literal /ɡli/ sequence, including *glicine* /ˈɡlitʃine/. Therefore `gli` cannot
be converted correctly without checking its context.

### S

- `ss` is always long voiceless /ss/: *rosso* /ˈrosso/.
- `s` before a voiceless consonant is normally /s/: *spesa*, *stanco*,
  *vespa* /ˈvɛspa/.
- `s` before a voiced consonant is normally /z/: *sbaglio* /ˈzbaʎʎo/,
  *sveglia* /ˈzvɛʎʎa/.
- Word-initial `s` before a vowel is normally /s/.
- A single intervocalic `s` can be /s/ or /z/ depending on the word and the
  speaker's regional standard. For example, *cosa* is commonly /ˈkɔza/.

Because ordinary spelling does not reliably distinguish intervocalic /s/ from
/z/, a dictionary or lexical override is required.

### Z

`z` and `zz` represent the affricates /ts/ or /dz/, not the simple English /z/.
The choice is partly lexical and is not reliably recoverable from spelling:

- *stazione* /statˈtsjone/
- *zio* /ˈtsio/
- *zero* /ˈdzɛro/
- *zanzara* /dzanˈdzara/

Intervocalic affricates are normally long in the reference pronunciation even
when conventions differ over exactly where to place the IPA length mark. Use a
dictionary for unfamiliar words.

### R

Italian /r/ is made with the tongue tip at the alveolar ridge. A single `r` is
often a tap [ɾ] between vowels, while initial `r`, consonant clusters, and `rr`
can have a stronger trill [r]. The important contrast is short versus long:
*caro* /ˈkaro/ and *carro* /ˈkarro/. An English approximant `r` is not the
target sound.

### H, Q, and other useful patterns

- `h` is silent. In `ch` and `gh` it preserves hard /k, ɡ/ before `e i`; in
  *ho, hai, ha, hanno* it distinguishes spelling but adds no sound.
- `qu` is normally /kw/: *questo* /ˈkwesto/. Some words spell the same sound
  with `cu`, as in *cuore* /ˈkwɔre/.
- A nasal assimilates to the place of a following consonant in connected
  speech: for example, /n/ is commonly [m] before /p b/ and [ŋ] before /k ɡ/.
  A broad learner transcription may leave this predictable detail unmarked.

## Double consonants

Consonant length is contrastive and must never be discarded by the phonetic
helper:

- *pala* /ˈpala/ "shovel" versus *palla* /ˈpalla/ "ball"
- *sete* /ˈsete/ "thirst" versus *sette* /ˈsɛtte/ "seven"

For a stop or affricate, hold the closure before release. For a continuant such
as /s, f, l, r, m, n/, sustain the sound longer. Several consonants are
regularly long between vowels in Standard Italian even when the spelling uses a
digraph or trigram: notably /ʃʃ/, /ɲɲ/, /ʎʎ/, and the dental affricates.

## Stress

Every independent Italian word has lexical stress. Penultimate stress is the
most common pattern, but it is not a dependable rule for generating exact
pronunciation from arbitrary text.

- Penultimate: *ragazzo* /raˈɡattso/, *parlare* /parˈlare/
- Antepenultimate: *tavolo* /ˈtavolo/, *telefono* /teˈlɛfono/
- Final, normally written: *città* /tʃitˈta/, *perché* /perˈke/
- Stress can distinguish words: *àncora* "anchor" versus *ancóra* "again"

When stress is not written, use a lexical pronunciation source. A fallback may
guess penultimate stress, but the UI must describe that result as approximate.

## Rhythm, connected speech, and TTS

Italian is commonly described as syllable-timed, but this is a rhythmic
tendency, not a command to make every syllable exactly equal. Stressed open
syllables may be longer, geminate consonants consume extra time, and normal
speech includes coarticulation.

In Central and standard-oriented pronunciation, certain words can trigger
*raddoppiamento fonosintattico*: the initial consonant of the next word is
lengthened even though the spelling does not show it. A familiar example is
*a casa*, often realized approximately [akˈkasa]. Its distribution varies by
region and lexical context. A word-level helper may omit it, but a
sentence-level helper should not claim to be a narrow transcription if it does.

TTS systems also vary in voice, region, speaking rate, and connected-speech
behavior. The helper should match the target phonemes and stress; it should not
promise an exact acoustic rendering of every TTS voice.

## Learner-respelling standard

The phonetic helper should be generated from a validated pronunciation, not
directly from spelling. Use these conventions consistently:

- Hyphens separate audible syllables.
- Capital letters identify the stressed syllable.
- `ah` = /a/, `é` = /e/, `è` = /ɛ/, `ee` = /i/, `ó` = /o/, `ò` = /ɔ/,
  and `oo` = /u/.
- `y` = /j/ and `w` = /w/.
- `ch` = /tʃ/, `j` = /dʒ/, `sh` = /ʃ/, `ly` = /ʎ/, `ny` = /ɲ/.
- `ts` = /ts/ and `dz` = /dz/.
- Preserve a doubled consonant in the respelling and add a short note such as
  "hold t" or "hold ly" when the spelling would not make the timing obvious.
- Do not use English `ay` or `oh` without explicitly stating that the Italian
  vowel is pure and has no final /j/ or /w/ glide.
- If stress, `e/o` quality, `s`, `z`, or vowel grouping is unknown, show IPA as
  approximate or omit the helper until a lexical pronunciation is available.

### Validated examples

| Italian | Broad IPA | Learner helper | Important detail |
|---|---:|---|---|
| *ciao* | /ˈtʃao/ | `CHOW` | approximate English cue; one syllable |
| *cane* | /ˈkane/ | `KAH-né` | closed /e/ |
| *bello* | /ˈbɛllo/ | `BÈL-loh` | open /ɛ/; hold `l` |
| *cosa* | /ˈkɔza/ | `KÒ-zah` | open /ɔ/; voiced /z/ |
| *vespa* | /ˈvɛspa/ | `VÈS-pah` | /s/, not /z/, before /p/ |
| *gnocchi* | /ˈɲɔkki/ | `NYÒK-kee` | hold /k/ |
| *famiglia* | /faˈmiʎʎa/ | `fah-MEE-lyah` | hold the palatal `ly` |
| *gli* | /ʎi/ | `lyee` | final /i/ is pronounced |
| *pesce* | /ˈpeʃʃe/ | `PÉSH-sheh` | /ʃ/ is long between vowels |
| *sciare* | /ʃiˈare/ | `shee-AH-ré` | pronounced /i/ plus hiatus |
| *stazione* | /statˈtsjone/ | `staht-TSYÓ-neh` | long /ts/ and /j/ glide |
| *spiaggia* | /ˈspjaddʒa/ | `SPYAH-jah` | two syllables; hold the /dʒ/ |
| *perché* | /perˈke/ | `pehr-KÉ` | final stress; closed /e/ |
| *caffè* | /kafˈfɛ/ | `kahf-FÈ` | final stress; open /ɛ/; hold /f/ |

The first example, *ciao*, exposes a limitation of English respelling: `CHOW`
is easy to read but only approximates the Italian vowel sequence. The IPA and
audio resolve that ambiguity. The software should therefore display IPA
alongside the helper.

## Implementation requirements for a phonetic helper

1. Normalize punctuation and apostrophes without discarding written accents.
2. Tokenize text while retaining word boundaries.
3. Look up curated whole-word pronunciation first. Store broad IPA, stress,
   syllable boundaries, and the learner helper together.
4. Apply spelling rules only when no lexical entry exists.
5. Mark rule-generated stress and ambiguous `e/o`, `s`, `z`, or hiatus as
   uncertain rather than inventing precision.
6. Preserve consonant length, including contextually long /ʃʃ, ɲɲ, ʎʎ/ and
   affricates.
7. Generate the learner helper from phonemes and stress, not by mechanically
   replacing letters.
8. Treat connected-speech processes as a separate sentence-level layer.
9. Test every vocabulary item against the same TTS voice used by the
   application, while recognizing legitimate regional voice variation.

## Sources

- RAI, [Dizionario italiano multimediale e multilingue d'ortografia e di
  pronunzia (DOP)](https://www.dizionario.rai.it/)
- Treccani, [Vocali](https://www.treccani.it/enciclopedia/vocali_%28Enciclopedia-dell%27Italiano%29/)
- Treccani, [Consonanti](https://www.treccani.it/enciclopedia/consonanti_%28Enciclopedia-dell%27Italiano%29/)
- Treccani, [Palatali](https://www.treccani.it/enciclopedia/palatali_%28Enciclopedia-dell%27Italiano%29/)
- Treccani, [Accento grafico](https://www.treccani.it/enciclopedia/accento-grafico_%28Enciclopedia-dell%27Italiano%29/)
- Treccani, [`-gl-` prontuario](https://www.treccani.it/enciclopedia/gl-prontuario_%28Enciclopedia-dell%27Italiano%29/)
- Treccani, [`-gn-` prontuario](https://www.treccani.it/enciclopedia/gn-prontuario_%28Enciclopedia-dell%27Italiano%29/)
- University of Pavia Language Centre,
  [Italian Phonetics](https://cla.unipv.it/EN/?page_id=53209)
- University of Oxford,
  [A Short Guide to Italian Phonetics and Phonology](https://www.ling-phil.ox.ac.uk/romance-linguistics/assets/uploads/paoli/Booklet_P%26P_right.pdf)
- University of Turin LFSAG,
  [Italian pronunciation resources](https://www.lfsag.unito.it/phoneit/index_en.html)
