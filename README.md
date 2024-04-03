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

The indicators are applied to every text in the input. They have their own score that can be consulted in the final ouput. Each one of them is calculated in a different way and has a particular role.

### Language probability

It is calculated using the language score that _>>LANGUAGE_DETECTOR<<_ gives to every text segment in this way:


`correct_characters_score / (correct_characters + wrong_characters_score)*10`

- __correct_characters_score:__ number of word characters multiplied by the language probability given to each segment if the detected language is the target language.
- __correct_characters:__ number of word characters if the detected language is the target language.
- __wrong_characters_score:__ number of word characters multiplied by the language probability given to each segment if the detected language is __not__ the target language.

This score is intended for not be penalized by short segments which seem to be header or footer menus, listing of social media, collaborator partners, etc. These cases are troublesome for the language detection, they are usually detected as English or other random language. For this reason, segments with _n_ or less word characters are ignored in this processing. _n_ is different according every language, 25 is considered the standard.

The language detection score has, moreover, some bias that makes differences between scores given to the segments depending on the language. To fix this bias we selected a sample of each language and processed them to obtain the language score. The median of the best 20% scored documents was selected as support point. The number obtained in the Spanish sample (8.0) has been used to rescale all language scores. For example, Urdu got a 4.6 score, this is rescaled to 8.0, so an 3.5 would be a 6.0 (3.5*8.0/4.6).




### Urls, numbers, punctuation, repeated segments
These scores should not be considered as a qualification score. They are intended as a penalty punctuation from 0 to 10. The 10 punctuation in any of these indicators means that the text is enought good to not be penalized, less than 8 will have an important effect to the final score and less than 5 punctuation will penalize severely the qualification of the text.

#### Urls
To determinate the number of urls we look for "www." or "http" strings in the whole text. We search the ratio between all non space characters and the number of urls:

`number_of_urls/non_space_characters * 100`

We selected an admissible and a maximum ratio for every language, English has for example a 0.3% and 2.0% respectively. Admissible ratio or less is considered a 10 score. Higher ratios will be penalized until reaching the maximum (or more) which are consireded a 0 score:

| Url score  |    Ratio      |
|---|---|
| 10 | 0.3% or less |
| 10 → 0 | 0.3% → 2.0% |
| 0 | +2.0% |

#### Numbers

The score of numbers is used to determinate the excess presence of number characters in the text. It is calculated comparing the ratio of numbers and word characters:

`count_of_numbers/word_characters * 100`

The applicated traduction for every ratio is variable depending on the language. For example in English we assign this score:

| Number score  |    Ratio      |
|---|---|
| 10 | 1.1% or less |
| 10 → 7 | 1.1% → 8.8% |
| 7 → 5 | 8.8% → 13.6% |
| 5 → 0 | 13.6% → 28.8% |
| 0 | +28.8% |

#### Punctuation, emojis, separators, etc.
This score is used to penalize texts with too much or too little amount of punctuation (emojis, separators, etc.). The ratio is calculed this way:

`punctuation_characters/non_space_characters`

As other scores the proportion considered good or bad is language dependant. In English we give these score to this proportions:

| Punctuation score  |    Ratio      |
|---|---|
| 10 | 1.1% → 3.1% |
| __Too much__  | |
| 10 → 7 | 3.1% → 10.2% |
| 7 → 5 | 10.2% → 15.2% |
| 5 → 0 | 15.2% → 30.4% |
| 0 | +30.4% |
| __Too few__  | |
| 10 → 5 | 1.1% → 0.8% |
| 5 → 0 | 0.8% → 0% |

#### Repeated segments
This score uses the proportion of repeated segments as a punctuation from 0 to 10. Short segments are ignored as it was explained in the language score processing.


### Big segments and largest segments
These two scores do not penalize the final qualification number. It is only used to benefit those texts that contains some considerably big segments in the target language. These consist in a punctuation from 0 to 10. 
A text will recieve a score point for every big segment until 10 with respect to the big segment score. The estimation of length of a big segment is language dependant and it is mesured using only the word character. For example, in English a 232 word characters segment is considered in this score.

In the other hand, talking about the largest segment score, it is used to mesure the texts that contains almost one very big segment in the target language. The length needed to consider a very big segment is also language dependant. In English we used 464 (or less) and 929 (or more) word characters as a point of reference for our minimum an maximum numbers to adjudicate from 0 to 10. If there are more than one of these segments, we use a average of them.



### Qualification score
The final score is a summary of the others. The language score is used as a base number. This number is multiplied by the negative scores (urls, numbers, punctuation, repeated segments) and then the positive scores are added (big segments and largest segments), all these scores are rescaled to 1. The calculation is done this way:

`((language_score*0.4+6) * url_score * punctuation_score * numbers_score * repeated_score)*0.9 + big_segments + largest_segments`

At this stage the language score is used partially because of some problems with the language detector.

## Usage


## Future improvements

