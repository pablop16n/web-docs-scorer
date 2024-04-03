# Quality text tagger


## Description

Quality text tagger is an application that assigns valoration scores (0-10) to given texts in any language supported by _>>LANGUAGE_DETECTOR<<_. It is specifically adjusted for crawled data in the current stage. The score given by the application is obtained by using several indicators:

- __language probability__
- ratio of __urls__
- ratio of __numbers__
- ratio of emojis, separators or __punctuation__ characters
- ratio of __repeated segments__
- presence of __big text segments__ in the target language
- length of __largest text segments__

The indicators has their own score and they can be consulted in the final ouput. Each one of them is calculated in a different way and has a particular role.

### Language probability
The language score is used as a base number which the other scores modify to obtain the final qualification score.

It is calculated using the language probability that _>>LANGUAGE_DETECTOR<<_ gives to every text segment in this way:


`correct_characters_score / (correct_characters + wrong_characters_score)*10`

- __correct_characters_score:__ number of word characters multiplied by the language probability given to each segment if the detected language is the target language.
- __correct_characters:__ number of word characters if the detected language is the target language.
- __wrong_characters_score:__ number of word characters multiplied by the language probability given to each segment if the detected language is __not__ the target language.

This score is intended for not be penalized by short segments which seem to be header or footer menus, listing of social media, collaborator partners, etc. These cases are troublesome for the language detection, they are usually detected as English or other random language. For this reason, segments with _n_ or less word characters are ignored in this processing. _n_ is different according every language, 25 is considered the standard.

The language detection score has, moreover, some bias that makes differences between scores given to the segments depending on the language. To fix this bias we selected a sample of each language and processed them to obtain the language score. The median of the best 20% scored documents was selected as support point. The number obtained in the Spanish sample (8.0) has been used to rescale all language scores. For example, Urdu got a 4.6 score, this is rescaled to 8.0, so an 3.5 would be a 6.0 (3.5*8.0/4.6).




### Urls, numbers, punctuation, repeated segments
These scores however should not be considered as a qualification score. They are intended as a penalty punctuation from 0 to 10. The 10 punctuation means that the text enought good at this



### Big segments
blabla

### Largest segments
blabla

## Usage
Use examples liberally, and show the expected output if you can. It's helpful to have inline the smallest example of usage that you can demonstrate, while providing links to more sophisticated examples if they are too long to reasonably include in the README.

