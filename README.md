# Quality text tagger


## Description

Quality text tagger is an application that assigns valoration scores (0-10) to given texts in any language supported by _>>LANGUAGE_DETECTOR<<_. It is specifically adjusted for crawled data in the current stage. The score given by the application is obtained by using several indicators:

- __unified language probability__ (language_score)
- ratio of __urls__ (urls_score)
- ratio of __numbers__ (numbers_score)
- ratio of __punctuation__ characters (punctuation_score)
- ratio of __emojis, non word punctuation, separatos, etc.__ characters (bad_chars_score)
- ratio of __repeated segments__ (repeated_score)
- presence of __big text segments__ in the target language (big_segments_score)
- length of __largest text segments__ (largest_segments_score)

The indicators are applied to every text in the input. These indicators have their own score that can be consulted in the final ouput. Each one of them is calculated in a different way and has a particular role in the final score (qualification_score). We use the ratios between, for example, numbers and word characters to asign a score to `numbers_score`. Ratios are manually selected based on crawled texts from HPLT 1.2v.

### Language score (language_score)

It is calculated using the language identification label that _>>LANGUAGE_DETECTOR<<_ gives to every text. Segments whose label is the expected one are considered correct and segments with a different label are considered wrong. We use the alphabetic or word characters to obtain a proportion of correct and incorrect characters from 0 to 10:


`correct_characters / (correct_characters + wrong_characters) * 10`

This score is not sensitive to short segments, which seem to be header or footer menus, listing of social media, collaborator partners, etc. These strings are troublesome for the language detection, they are usually detected as English or other random language. For this reason, segments with _n_ or less word characters are ignored in this processing. _n_ is different according every language, 24 is considered the number for English.

### Big segments and largest segments (big_segments_score and largest_segments_score)
These two scores consist in a punctuation from 0 to 1 that aim to determinate the presence of big groups of text in the target language.

For the big segment score, a text will recieve a 0.1 score point for every big segment until 1. The estimation of length of a considered big segment is language dependant and it is mesured using only the word character. For example, in English a 232 word characters segment is considered within this score.

In the other hand, talking about the largest segment score, it is used to mesure the documents that contains almost one very big segment in the target language. The length needed to consider a very big segment is also language dependant. In English we used 464 (or less) and 929 (or more) word characters as a point of reference for our minimum an maximum numbers to adjudicate from 0 to 1. If there are more than one of these segments, we use an average of them.

### Penalty scores: Urls, numbers, punctuation, bad_chars, repeated segments
These scores should not be considered as a positive score. They are intended as a penalty punctuation from 0 to 1. The 1 punctuation in any of these indicators means that the text is enought good to not be penalized, less than 0.8 will have an important effect to the final score and less than 0.5 punctuation will penalize severely the qualification of the text.

#### Urls (urls_score)
To determinate the number of urls we look for "www" or "http" strings in the whole text. We search the ratio between the number of urls and the number of segments in the text, this ignore short segments, like it is done in `language_score`. The urls_score is language independant and is calculated as follows:

`number_of_urls / number_of_segments * 100`

We selected an admissible and a maximum ratio, 20% or less is not considered punishable (1 score). Higher ratios will be penalized until reaching the maximum (or more) which are consireded a 0 score:

| Url score  |    Ratio      |
|---|---|
| 1 | <5% |
| 1 → 0.5 | 5% → 30% |
| 0.5 → 0 | 30% → 100% |
| 0 | >100% |

#### Numbers (numbers_score)

The score of numbers is used to determinate the excess presence of number characters in the text. It is calculated comparing the ratio of numbers and word characters:

`numbers / word_characters * 100`

The applicated traduction for every ratio is variable depending on the language. For Spanish we assign this scores:

| Number score  |    Ratio      |
|---|---|
| 1 | <1% |
| 1 → 0.7 | 1% → 10% |
| 0.7 → 0.5 | 10% → 15% |
| 0.5 → 0 | 15% → 30% |
| 0 | >30% |

#### Punctuation (punctuation_score)
This score is used to penalize texts with too much or too little amount of punctuation. The ratio is calculed this way:

`punctuation_characters / word_characters * 100`

As other scores the proportion considered good or bad is language dependant. In Spanish we give the next scores to these proportions:

| Punctuation score  |    Ratio      |
|---|---|
| 1 | 0.9% → 2.5% |
| __Too much__  | |
| 1 → 0.7 | 2.5% → 9% |
| 0.7 → 0.5 | 9% → 13% |
| 0.5 → 0 | 13% → 25% |
| 0 | >30.4% |
| __Too few__  | |
| 0 → 0.5 | 0.9% → 0.5% |
| 0.5 → 0 | 0.5% → 0.3% |
| 0 | <0.3% |

#### Emojis, separators, non word punctuation (bad_chars_score)

Bad_chars_score is used to penalize texts with undesireded characters:

`numbers / word_characters * 100`

The applicated traduction for every ratio is variable depending on the language. For Spanish we assign this scores:

| Bad chars score  |    Ratio      |
|---|---|
| 1 | <1% |
| 1 → 0.7 | 1% → 2% |
| 0.7 → 0.5 | 2% → 6% |
| 0.5 → 0 | 6% → 10% |
| 0 | >10% |

#### Repeated segments (repeated_score)
This score uses the proportion of repeated segments. Short segments are ignored using the same logic as the language score processing. For example, 0% of repeated segments will get a 1 score, 20% of repeated segments will have a 0.8 and 100% of repeated segments will recieve a 0 score.

#### Penalty score calculation (penalty_score)
The penalty_score unify the previous scores: url_score, punctuation_score, bad_chars_score, numbers_score and repeated_score. To calculate it the two lowest values are multiplied with the average of the rest of values:

`first_minor_value * second_minor_value * average(other_values)`


### Language adaptation of the scores (punctuation_score, bad_chars_score, numbers_score, big_segments_score, largest_segments_score and 'short segments')
We stablished, first of all, the desidered ratios for each indicator (numbers, punctuation, etc.) in Spanish, using a sample of texts from HPLT v1.2. These ratios will be valid only for this language, so an adaptation method is needed.

To adapt the scores to particular languages we used the scores provided by the _>>LANGUAGE_DETECTOR<<_ in a sample of at least 10k documents per language. The 50% best language scored documents are selected to extract the punctuation, bad characters and numbers ratio. We extract the median of these frame of filtered documents with `language_adaptation/extract_ratios.py`, which are saved in `language_adaptation/medians_language.csv`. These data is used in the main script (`crawled_text_qualifier.py`) to create an equivalence. For example, the median of both Russian and Spanish regarding bad chars is the same (0.8), so they will use the logic as we shown in the table of bad chars. The punctuation ratio is somewhat different, 3.2 for Russian and 2.4 in Spanish, that means that the 30.4% ratio of `punctuation/word characters` that we presented as our maximum, equivalent to score -1, must be adapted. We used a cross-multiplication for that: `(3.2*30.4)/2.4 = 40.5%`. The adapted table for Russian in respect to punctuation_score is thus as follows:

| Punctuation score  |    Ratio Spanish      | Ratio Russian |
|---|---|---|
| 1 | 0.9% → 2.5% | 1.2% → 3.3% |
| __Too much__  | | |
| 1 → 0.7 | 2.5% → 9% | 3.3% → 12% |
| 0.7 → 0.5 | 9% → 13% | 12% → 17.3% |
| 0.5 → 0 | 13% → 25% | 17.3% → 33.3% |
| 0 | >30.4% | 40.5% |
| __Too few__  | |
| 0 → 0.5 | 0.9% → 0.5% | 1.2% → 0.7% |
| 0.5 → 0 | 0.5% → 0.3% | 0.7% → 0.4% |
| 0 | <0.3% | <0.4% |



### Qualification score
The final score is a summary of the others. The language score has an initial weigth of 80% (`language_score*0.8`). The scores about segments length add the missing 20% (`+ big_segments_score + largest_segments_score`). The resulting number is multiplied by a custom mean of the rest of scores, those that we called penalty scores, using the `penalty_score`. The calculation is done this way:

`(language_score*0.8 + big_segments_score + largest_segments_score) * penalty_score`


#### Use example

The document named `example/zh_hplt_1_2_952203152.txt` has been analized with this application. It contains a crawled text from HPLT v1.2 that obtained a __score of 1.5__:

[...]
 
www.34449com-www,67617,com  

首页 | 认证专区 | 论坛 | 博客 | 人才 | 频道 | 名人堂 | 自测 | 文库 | 沙龙  

博客首页往日推荐排 行 榜博客文集专题荟萃专  家认证专区  

8686123白小姐9999911111香港曾半仙www.66575.com472222刘伯
温开奖www,df011,comwww993997.com

全部分类

数据库

[...]

This text is considered good in some scores. Language, punctuation and bad chars are as expected and there is no repeated segments:
| Score  |    Value      |
|---|---|
| language_score | 8.0 |
| url_score | 0.44 |
| punctuation_score | 0.9 |
| bad_chars_score | 1 |
| numbers_score | 0.56 |
| repeated_score | 1 |
| big_segments_score | 0.1 |
| largest_segments_score | 0.0 |

The length scores are empty and the language score is not perfect. That makes the calculation start poorly:


|(language_score*0.8 + big_segments_score + largest_segments_score)| Result |
|---|---|
|8 * 0.8 + 0.1 + 0| 6.5 |


But the main problem comes with the excess of numbers and urls in the moment we add the penalty_score:

|first_minor_value * second_minor_value * average(other_values)| Result |
|---|---|
|0.44 * 0.56 * 0.97| 0.24 |

Note: average(other_values) = (0.9+1+1)/3 = 0.97

So the penalty_score will reduce the base (6.5) drastically:
|(language_score*0.8 + big_segments_score + largest_segments_score) * penalty_score| Result |
|---|---|
| 6.5 * 0.24| 1.5 |



## Usage

#### crawled_text_qualifier.py (main script)

Parameters 
- **--input** directory with jsonl files provided by _>>LANGUAGE_DETECTOR<<_
- **--output:** existing directory

Output
- will create one csv for each jsonl file.
- columns: ...

Requisites

- document `./language_adaptation/medians_language.csv` created by `./language_adaptation/extract_ratios.py`
- libraries ...

#### qualifications_score_charts.py
Parameters 
- **--input** directory with csv files created by `crawled_text_qualifier.py`
- **--output:** existing directory

Output
- HTML document with histograms about all languages present in the input



## Future improvements



