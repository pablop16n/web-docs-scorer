# Quality text tagger

Quality text tagger is an application that assigns a score on a 10-point scale to a document. The current implementation assumes that the document contains information about language identification at document and segment level, the content itself and segment boundaries which roughly correspond to paragraphs. 

Our goal is to distinguish among good and bad documents from crawled websites. Good documents in our setting are those mainly made of linguistic data, containing a big portion of running text divide among long and well constructed paragraphs. Conversely, we consider bad those documents mainly made of non-linguistic characters (like code or emojis) or which show an excess of numbers, puctuation, repetitions, etc.  

 
## How does the tagger work

In order to assign a score (**quality_score**) on a 10-point scale, the quality text tagger computes several subscores over the content and metadata of the document (higher is always better):

| Subcore  |  Based on   |  Scale   | 
|---|---|---|
| language_score | mean of language probability (segments vs documents) | 0 - 10 | 
| big_segments_score | presence of big text segments in content | 0 - 1 | 
| largest_segments_score | length of largest text segments | 0 - 1 | 
| urls_score | ratio of urls | 0 - 1 | 
| numbers_score | ratio of number characters | 0 - 1 | 
| punctuation_score | ratio of punctuation characters | 0 - 1 | 
| bad_chars_score | ratio of bad characters: emojis, non word punctuation, separators, etc. | 0 - 1 | 
| repeated_score | ratio of repeated segments | 0 - 1 | 

A detailed description about these subscores is given in section [Computing subscores](https://gitlab.prompsit.com/hplt/quality-text-tagger/-/blob/main/README.md#computing-subscores). 

The **quality_score** will be computed using these subscores. 

### Computing the quality_score

processed with: `crawled_text_qualifier.valorate_text()`

The quality score takes the above described set of subscores computed over a document and uses them as follows:

1. First, a **basic score** is obtained by adding the subscores that represent positive aspects of the document content: the _language_score_ to which we give a weigth of 80% (`language_score * 0.8`), the _big_segments_score_ and the _largest_segments_score_.

`basic score`= `language_score * 0.8 + big_segments_score + largest_segments_score`

2. Then, we use the rest of the subscores which represent negative aspects of the document content (_urls_score_, _numbers_score_, _punctuation_score_, _bad_chars_score_, _repeated_score_) to compute a **penalty_score** using the following formula:

`penalty score` = `first_minor_negative_subscore_value * second_minor_negative_subscore_value * average (remaining_negative_subscores_values) `

Please, see section [Computing the penalty_score](https://gitlab.prompsit.com/hplt/quality-text-tagger/-/blob/main/README.md#computing-the-penalty_score) for more details.

3. Finally, we get the **quality_score** by multipliying the **basic score** by the **penalty_score**: 

`quality score` = `basic score * penalty score`


### An example of the quality_score

We show a practical example on how the **quality_score** is computed and its meaning for a document from the HPLT v1.2 Italian dataset. 

This is an excerpt of a whole document from this dataset that can be found in `example/example1.jsonl`:

> [...]
> 
> _La frase con 把 è usata per rispondere:_
> 
> _Dove disporre una persona o una cosa (collocazione spaziale come conseguenza dell’azione)?_
> 
> _Come disporre una persona o una cosa (disposizione con la modalità espressa dall’azione come conseguenza)_
> 
> _Ti interessa saperne di più? Continua a seguirmi, e fai le tue domande che non credo ..._ 
> 
> [...]


From this document, we get these subscores: 

| Subcores  |    Value      |
|---|---|
| language_score | 9.9 |
| big_segments_score | 0.4 |
| largest_segments_score | 1.0 |
| url_score | 1.0 |
| punctuation_score | 1.0 |
| bad_chars_score | 1.0 |
| numbers_score | 0.92 |
| repeated_score | 0.96 |

The document **quality score** is computed using these subscores values as above explained:  

**basic score** = 9.9 x 0.8 + 0.4 + 1 = **9.32**

**penalty score** = 0.92 x 0.96 x ((1+1+1)/3) =  **0.88**

**quality score** = 9.32 x 0,88 = **8.2** 


This means that we have a good document (**quality_score** = 8.2/10), undoubtedly in Italian (_language_score_ = 9.9/10). It probably contains a considerable amount of linguistic data in one or two segments (_largest_segment_score_ = 1/1), but not too many long segments (_big_segments_score_ = 0.4/1).

The document does not to contain url, punctuation or bad characters noise (_url_score_ = 1/1, _punctuation_score_ = 1/1, _bad_chars_score_ = 1/1). It contains a small excess of numbers (_numbers_score_ = 0.92/1), which could be due to the presence of a calendar present in the text:

[...] _Gennaio 2022 \n Giugno 2021 \n Marzo 2021 \n Novembre 2020 \n Ottobre 2020..._ [...]

And it has a few repeated segments (_repeated_score_ = 0.96/1) of recurrent headers or titles:

[...] _Grammatica, livello avanzato ... Grammatica, livello avanzato_ [...]


### Another example of the quality_score

The following excerpt belongs to the file `example/example2.txt`, a Chinese document from the HPLT v1.2 dataset which got a **quality_score** of 1.5:

> [...]
>  
> www.34449com-www,67617,com  
> 
> 首页 | 认证专区 | 论坛 | 博客 | 人才 | 频道 | 名人堂 | 自测 | 文库 | 沙龙  
> 
> 博客首页往日推荐排 行 榜博客文集专题荟萃专  家认证专区  
> 
> 8686123白小姐9999911111香港曾半仙www.66575.com472222刘伯
> 温开奖www,df011,comwww993997.com
> 
> 全部分类
> 
> 数据库
> 
> [...]


We compute the subscores: 

| Subscore  |    Value      |
|---|---|
| language_score | 8.0 |
| big_segments_score | 0.1 |
| largest_segments_score | 0.0 |
| url_score | 0.44 |
| punctuation_score | 0.9 |
| bad_chars_score | 1 |
| numbers_score | 0.56 |
| repeated_score | 1 |

This text seems to be made of mainly short sentences (note the very low values for big_segments_score and largest_segments_score) and even from some mix of languages according to the language identifier. This makes the basic score already a low one: 

|basic score| Result |
|---|---|
|8 * 0.8 + 0.1 + 0| 6.5 |


The document does not seem to have bad punctuation, or characters and it does not contain repeated sentences, but it has an excess of numbers and urls. This impacts highly the penalty_score value:

|penalty score| Result |
|---|---|
|0.44 * 0.56 * 0.97| 0.24 |

Thus, the final qualty_score is also very low:

|basic score * penalty score| Result |
|---|---|
| 6.5 * 0.24| 1.5 |

This document is considere an undesirable document. 

## Usage

#### crawled_text_qualifier.py (main script)

Parameters 
- **--input** directory with jsonl files provided by _>>LANGUAGE_DETECTOR<<_
- **--output:** existing directory

Output
- will create one csv for each jsonl file.
- columns: quality_score, language_score, url_score, punctuation_score, bad_chars_score, numbers_score, repeated_score,n_big_segments_score, great_segment_score

Requisites

- document `./language_adaptation/medians_language.csv` created by `./language_adaptation/extract_ratios.py` with samples of data

#### quality_score_charts.py

Parameters 
- **--input** directory with csv files created by `crawled_text_qualifier.py`
- **--output:** existing directory

Output
- HTML document with histograms about all languages present in the input



## Computing the penalty_score

processed with: `crawled_text_qualifier.custom_mean()`

The subscores used to compute the **penalty_score** are: urls_score, numbers, punctuation, bad_chars and repeated segments

These subscores represent negative aspects of the document content. They range on a scale from 0 to 1, where 1 means that no penalization should be applied. Bellow 1, 0.8 will have an important effect in the final score and less than 0.5 will penalize it severely. A 0 value in any of these scores thus means that the resulting value will be 0 in any case.


To compute the penalty score, the two lowest values from the above mentioned subsscores are multiplied by the average of the rest of values:

`first_minor_value * second_minor_value * average(other_values)`

We prefer this solution to a simple average because the aim of these scores is to advertise about documents that stand out of the desidered ratios. A classical average would overshadow low values, which are the most precious to our goal, and a simple multiplication of all scores would make it hard to work with more than 4 or 5 penalty variables.


## Computing subscores

### language_score

processed with: `crawled_text_qualifier.valorate_lang()`

The _language_score_ is a value from 0 to 10, that descrives the amount of segments in the correct language. It is calculated using the language identification label that _>>LANGUAGE_DETECTOR<<_ gives to every segment of the text. The language detector also asigns a tag to the complete document, which is considered the main language. Segments whose label agrees with the main language one are considered correct and segments with a different label are intended as wrong. We use the word characters to obtain a proportion of correct and incorrect ones:


`correct_characters / (correct_characters + wrong_characters) * 10`

This score is not sensitive to short segments, which seem to be header or footer menus, listing of social media, collaborator partners, etc. These strings are troublesome for the language detector, because they are usually classified as English or other random language. For this reason, segments with _n_ or less word characters are ignored in this processing. The _n_ value is different according every language. For example, 25 is considered the minimum number for Spanish.

### big_segments_score and largest_segments_score

processed with: `crawled_text_qualifier.valorate_big_texts()`

These two scores consist in a punctuation from 0 to 1 that aim to determinate the presence of big groups of word characters in the correct language.

For the _big_segments_score_, a document will recieve a 0.1 score point for every big segment, with a maximum of 1. The length of what we considered 'big segment' is language dependant and it is mesured using only the word characters value. In Spanish, we decided that a segment with more than 250 word characters is considered within this score, in English, for example, a higher of 232 value is enough.

In the other hand, talking about the _largest_segments_score_, it is used to mesure the documents that contains almost one very big segment in the target language. The length needed to consider a very big segment is also language dependant. In Spanish we used 625 (or less) and 1000 (or more) word characters as a point of reference for our minimum an maximum numbers to adjudicate from 0 to 1. If there are more than one of these segments, we use an average of them.




### urls_score

processed with: `crawled_text_qualifier.valorate_urls()`

To determinate the number of urls in the document we look for "www" or "http" strings in the whole text. We search the ratio between the number of urls and the number of segments in the text, this ignore short segments, like it is done in _language_score_. The _urls_score_ is language independant and is calculated as follows:

`number_of_urls / number_of_segments * 100`

We agree that documents with 5 or less urls each 100 segments is a enough good ratio, more than 5 must be penalized and 100/100 are usually worthless texts:

| Url score  |    Ratio      |
|---|---|
| 1 | <5 |
| 1 → 0.5 | 5 → 30 |
| 0.5 → 0 | 30 → 100 |
| 0 | >100 |

### numbers_score

processed with: `crawled_text_qualifier.valorate_numbers()`

The score of numbers is used to determinate the excess presence of number characters in the entire text. It is calculated comparing the ratio of numbers and word characters:

`numbers_characters / word_characters * 100`

The applicated traduction for every ratio is variable depending on the language. For Spanish we assign this scores:

| Number score  |    Ratio      |
|---|---|
| 1 | <1 |
| 1 → 0.7 | 1 → 10 |
| 0.7 → 0.5 | 10 → 15 |
| 0.5 → 0 | 15 → 30 |
| 0 | >30 |

### punctuation_score

processed with: `crawled_text_qualifier.valorate_punctuation()`

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
| 0 | >25% |
| __Too few__  | |
| 0 → 0.5 | 0.9% → 0.5% |
| 0.5 → 0 | 0.5% → 0.3% |
| 0 | <0.3% |

Not only too much punctuation is problematic, but also too few is undesired, because it could mean that the text crawled is an enumeration of tags, products, SEO phrases or other linguistically unstructured data.

### bad_chars_score

processed with: `crawled_text_qualifier.valorate_bad_chars()`

The _bad_chars_score_ is used to penalize texts with undesireded characters:

`bad_characters / word_characters * 100`

As the previous scores it is variable depending on the language. For Spanish we assign this scores:

| Bad chars score  |    Ratio      |
|---|---|
| 1 | <1% |
| 1 → 0.7 | 1% → 2% |
| 0.7 → 0.5 | 2% → 6% |
| 0.5 → 0 | 6% → 10% |
| 0 | >10% |

### repeated segments (repeated_score)

processed with: `crawled_text_qualifier.valorate_repeated()`

This score uses the proportion of repeated segments. Short segments are ignored using the same logic as the language score processing. For example, 0% of repeated segments will get a 1 score, 20% of repeated segments will have a 0.8 and 100% of repeated segments will recieve a 0 score.



## Adaptating subscores to different languages 

processed with: `language_adaptation.extract_ratios()`, `crawled_text_qualifier`

Some of the subscores used to get the quality_score are based on ratios that need to be computed for each language for optimal performance. These are: punctuation_score, bad_chars_score, numbers_score, big_segments_score, largest_segments_score and 'short segments'.


In our experiments, , as a first approach, we stablished the desidered ratios for each indicator (numbers, punctuation, etc.) in Spanish, using a sample of texts from HPLT v1.2. These ratios will be valid only for this language, so an adaptation method is needed.

To adapt the values to particular languages we used the scores and the labels provided by the _>>LANGUAGE_DETECTOR<<_ in a sample of at least 10k documents per language. The 50% best language scored documents are selected to extract the ratio of punctuation, bad characters and numbers. We extracted the median of these frame of filtered documents, which are saved in `language_adaptation/medians_language.csv`, with `language_adaptation/extract_ratios.py`. These data is used in the main script (`crawled_text_qualifier.py`) to create an equivalence of the data.


If the Spanish ratios-score logic is applied to other languages that differ significantly, the ratios would not fit correctly, as can be seen in these histograms. Most of the inputs in this sample would be undesirably penalized:

![alt text](example/spanish.png)
![alt text](example/korean_non_adapted.png)

To solve this problem we decided to use medians as a point of reference for move the scores to more correct ranges. In this case, Korean has a median of 7.3 and Spanish 2.4. We use this information to make a cross-multiplication so we get a new and adapted score-ratio relationship:

![alt text](example/korean_adapted.png)


Using another example, the median of both Russian and Spanish, regarding bad chars, is the same (0.8), so they will use the same logic as we shown in the table of bad chars. The punctuation ratio is somewhat different, 3.2 for Russian and 2.4 in Spanish, that means that the Spanish 0.9 ratio of the _punctuation_score_, that we presented as a perfect scored value (1), is not valid for Russian. The main script uses a cross-multiplication to solve this: 

`(3.2 * 0.9)/2.4 = 1.2`

Consequently, the adapted table for Russian in respect to _punctuation_score_ is as follows:

| Punctuation score  |    Ratio Spanish      | Ratio Russian |
|---|---|---|
| 1 | 0.9 → 2.5 | 1.2 → 3.3 |
| __Too much__  | | |
| 1 → 0.7 | 2.5 → 9 | 3.3 → 12 |
| 0.7 → 0.5 | 9 → 13 | 12 → 17.3 |
| 0.5 → 0 | 13 → 25 | 17.3 → 33.3 |
| 0 | >25 | >33.3 |
| __Too few__  | |
| 0 → 0.5 | 0.9 → 0.5 | 1.2 → 0.67 |
| 0.5 → 0 | 0.5 → 0.3 | 0.67 → 0.4 |
| 0 | <0.3 | <0.4 |

Not only the relative values are adapted (_punctuation_score_, _bad_chars_score_, _numbers_score_), also some absolute values need to be more flexible depending on the language. We use the punctuation ratios to transform the values of _big_segments_score_, _largest_segments_score_ and what we called 'short segments', which are ignored in somes scores. For example, Spanish use 1000 word characters as a reference for _largest_segments_score_ with a median of 2.4 in punctuation characters, in Japanese, with 6.5, 369 characters is enough according to the inverse cross-multiplication:

`2.4 * 1000 / 6.56.5`

The relationship is inversely proportional, the more punctuation each word characters, the less word characters the language will use on average.

## Glossary
- _document_: whole text of a crawled website
- _segment_: every string group between `\n` character
- _x type character_: see next table

| Name  |  Meaning   |  utf-8 ranges   |
|---|---|---|
|number character|Numbers in many languages|0030-0039, 0660-0669, 06F0-06F9, 0964-096F, 09F2-09F9, 0B66-0B77, 0BE6-0BFA, 0C66-0C6F, 0C78-0C7E, 0CE6-0CEF, 0D66-0D79, 0DE6-0DEF, 0E50-0E5B, 0EC0-0ED9, 1040-1049, 1090-1099, 1369-137C, 17E0-17E9, 1810-1819, 19D0-19DA, 1A80-1A99, 1B50-1B59, 1C40-1C49, 1C50-1C59, A830-A839, A8D0-A8D9, AA50-AA59|
|punctuation character|Most frequent linguistic punctuation|0021-0022, 0027-0029, 002C-002E, 003A-003B, 003F, 005B, 005D, 0060, 00A1, 00B4-00B5, 00B7, 00BF,0589-05C7, 0600-061F, 066A-066D, 06D4-06ED, 0700-070F, 1360-1368, 1800-180A, 1AB0-1AFF, 1C78-1C7F, 1CC0-1CC7, 1FBD-1FC1, 1FCD-1FCF, 1FDD-1FDF, 1FED-1FEF, 1FFD-2027, 3000-303F, 4DC0-4DFF, A6F0-A6F7, FE10-FE6F|
|bad character|Non typical linguistic punctuation, emojis, separators, etc.|0023-0026, 002A-002B, 002F, 003C-003E, 0040, 005C, 007C, 007E, 00A2-00B3, 00B8-00BE, 00D7, 00F7, 02B0-0385, 0483-0489, 0559-055F, 2010-2E52, 10000-1FFFF, A670-A67F, 3200-33FF|
|space character|White spaces, tabulations, new lines, etc.|0000-0020, 007F-00A0, 2B7E, 008A, 0088|
|word character|Characters that are used to create lexical units or words| Any character not in the other groups |

