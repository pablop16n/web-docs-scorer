# Quality text tagger

Quality Text Tagger is an application that analyzes monolingual documents (from crawled websites) and gives them a quality score that works as a measure of how good or bad the document is (see below). The score is on a  0 (really bad document) to 10 (very good document) scale, and it's obtained by taking into account textual indicators and metadata. 

Good documents (scores 5-10) are those mainly made of linguistic data, containing a large portion of running text distributed across long and well constructed paragraphs. Conversely, bad documents (scores 0-4) are mainly made of non-linguistic characters (like code or emojis) or contain an excess of numbers, puctuation symbols, segment repetitions, etc.  

Quality Text Tagger requires the input documents to be formatted in JSONL, containing the same fields as the documents in the HPLT 1.2 version (see an example of the format [here](https://hplt-project.org/datasets/v1.2)). The current implementation assumes that each document contains information about language identification (at document and segment level), and the text itself with segment boundaries (i.e. `/n`) which (roughly) correspond to paragraphs. 


# Table of contents

**[MBG]to do!**

 
## How does the tagger work

In order to give a **_quality_score_** to a document, the quality text tagger computes several subscores over its content and metadata. Note that higher is always better:

| Subcore  |  Based on   |  Scale   | 
|---|---|---|
| language_score | ratio of characters in the correct language vs. total characters | 0 - 10 | 
| big_segments_score | amount of long segments (alphabetic characters) | 0 - 1 | 
| largest_segments_score | length of largest text segments | 0 - 1 | 
| urls_score | ratio of URLs vs. total segments | 0 - 1 | 
| numbers_score | ratio of [numeric characters](https://gitlab.prompsit.com/hplt/quality-text-tagger/-/blob/main/README.md#glossary) vs. alphabetic characters| 0 - 1 | 
| punctuation_score | ratio of [punctuation characters](https://gitlab.prompsit.com/hplt/quality-text-tagger/-/blob/main/README.md#glossary) vs. alphabetic characters| 0 - 1 | 
| bad_chars_score | ratio of [bad characters](https://gitlab.prompsit.com/hplt/quality-text-tagger/-/blob/main/README.md#glossary) (emojis, non word punctuation, separators, etc.) vs. alphabetic characters | 0 - 1 | 
| repeated_score | ratio of repeated segments | 0 - 1 | 

A detailed description about these subscores is given in section [Computing subscores](https://gitlab.prompsit.com/hplt/quality-text-tagger/-/blob/main/README.md#computing-subscores). 


### Computing the _quality_score_

The  _quality_score_ is processed with `crawled_text_qualifier.valorate_text()`. It combines the aforementioned set of subscores as follows:

1. First, a **_basic_score_** is obtained by adding the subscores that represent positive aspects of the document content: 
  * _language_score_ 
  * _big_segments_score_
  * _largest_segments_score_

`basic_score = language_score * 0.8 + big_segments_score + largest_segments_score`

Note that the _language_score_ is weighted (since it scores from 0 to 10, while the other values score 0 to 1), so the maximum possible value of the _basic_score_ is 10.

2. Then, we use the rest of the subscores (which represent negative aspects of the document content) to compute a **_penalty_score_**:
  * _urls_score_
  * _numbers_score_
  * _punctuation_score_
  * _bad_chars_score_
  * _repeated_score_

`penalty_score = first_lowest_negative_subscore_value * second_lowest_negative_subscore_value * average (remaining_negative_subscores_values) `

`first_lowest_negative_subscore_value` and `second_lowest_negative_subscore_value` are the two subscores with the lowest values.  Please, see section [Computing the _penalty_score_](https://gitlab.prompsit.com/hplt/quality-text-tagger/-/blob/main/README.md#computing-the-penalty_score) for more details.

3. Finally, we get the final **_quality_score_** by multipliying the **_basic_score_** by the **_penalty_score_**: 

`quality score = basic score * penalty score`


### An example of the _quality_score_

In this section we show an example on how the **_quality_score_** is computed, and the meaning of its subscores. The document is extracted from the HPLT v1.2 Italian dataset, and can be found in `example/example1.jsonl`. An excerpt of the document is shown below:

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

As explained in the section above, the **_quality_score_** of the document is computed by using these subscores values:

**basic score** = (9.9 x 0.8) + 0.4 + 1 = **9.32**

**penalty score** = 0.92 x 0.96 x ((1+1+1)/3) =  **0.88**

**quality score** = 9.32 x 0,88 = **8.2** 

This means that this document a good document (**_quality_score_** = 8.2/1) that is clearly in Italian (_language_score_ = 9.9/10). It probably contains a considerable amount of textual data in some segments (_largest_segment_score_ = 1/1), but it only contains 4 long segments (_big_segments_score_ = 0.4/1).
[MBG] Plz explain a bit more what " contains a considerable amount of textual data in some segments" means. 

The document does not contain enough URLs, punctuation or bad characters noise to be penalized because of it (_url_score_ = 1/1, _punctuation_score_ = 1/1, _bad_chars_score_ = 1/1). It contains a small excess of numbers (_numbers_score_ = 0.92/1), which could be due to the presence of a calendar present in the text:

> [...] _Gennaio 2022 Giugno 2021 \n Marzo 2021 \n Novembre 2020 \n Ottobre 2020..._ [...]

The document also has some repeated segments (_repeated_score_ = 0.96/1) caused by recurrent headers or titles:

>[...] Grammatica, livello avanzato [...]
> Grammatica, livello avanzato [...]


### Another example of the _quality_score_

The following excerpt belongs to the file `example/example2.txt`, a Chinese document from the HPLT v1.2 dataset. The document got a **quality_score** of 1.5:

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

This text seems to be mostly made of short segments (note the very low values for _big_segments_score_ and _largest_segments_score_) and, according to the language identifier, with a part of the segments not in the document language. Because of this, the basic score is already low: 

|basic score| Result |
|---|---|
|8 * 0.8 + 0.1 + 0| 6.5 |


The document does not seem to have bad punctuation or bad characters, and it does not contain repeated sentences. However, it has an excess of numeric characters and URLs. This has a high impact on the _penalty_score_ value:
U
|penalty score| Result |
|---|---|
|0.44 * 0.56 * 0.97| 0.24 |

Thus, the final _quality_score_ is also very low:

|basic score * penalty score| Result |
|---|---|
| 6.5 * 0.24| 1.5 |

With such a low quality score, this document can be considered an undesirable document. 

## Usage

[MBG] Please give this section a format in the fashion of  https://github.com/bitextor/bicleaner?tab=readme-ov-file#parameters-1
(schematic + description + example)

#### crawled_text_qualifier.py (main script)

Parameters 
- **--input** directory with jsonl files provided by the language identifier
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

#### language_adaptation/extract_ratios.py

- **--input** directory with jsonl files with HPLT 1.2v like structure of key and values
- **--output:** existing directory

Output
- CSV that contains the medians of numbers, punctuation and bad characters ratios in every language present in the directory


## Computing the _penalty_score_

[MBG] Consider changing the name from "penalty score" to "booster", since it is actually multiplied by the first score instead of substracted from it (I got confused by the name)

The _penalty_score_  is obtained with `crawled_text_qualifier.custom_mean()` . The subscores used to compute the **_penalty_score_** are those that represent the negative aspects of the document:
  *  _urls_score_
  * _numbers_score_
  * _punctuation_score_
  * _bad_chars_score_
  * _repeated_score_

The _penalty_score_ ranges on a scale from 0 (the document is severely penalized and gets a final quality score of 0) to 1 (no penalization is applied).

To compute the _penalty_score_, the two lowest values from the aforementioned subsscores are multiplied by the average of the rest of values:

`first_lowest_value * second_lowest_value * average(other_values)`

We prefer this solution to a simple average because the aim of these scores is to warn about documents that stand out of the desired ratios: a simple average would overshadow low values (which are the most valuable to our goal), while a simple multiplication of all scores would make it hard to work with more than 4 or 5 penalty variables.


## Computing subscores

### language_score

The _language_score_ is processed with `crawled_text_qualifier.valorate_lang()`. It uses the information about language identification at segment and document level (provided as metadata in the input files) in order to get the ratio of [alphabetic characters](https://gitlab.prompsit.com/hplt/quality-text-tagger/-/blob/main/README.md#glossary) in the correct language. Segments whose language matches the document language are considered correct and segments with a different language are considered wrong. The _language_score_ is a value that ranges from 0 (worst score) to 10 (best score), and is computed as follows:

`correct_characters / (correct_characters + wrong_characters) * 10`

Segments below a certain length threshold are not taken into account to this metric, so this score is not sensitive to short segments (which often  to header or footer menus, social media listings, partners listings, etc.) These strings are troublesome for language identifiers as they are usually classified as English or other random language. The length threshold is different for each language. For example, 25 is considered the minimum acceptable number of characters for taking Spanish segments into account for this metric.

### big_segments_score and largest_segments_score

These two metrics are obtained with `crawled_text_qualifier.valorate_big_texts()`.  They get values between 0 and 1 that aim at determining the presence of large groups of alphabetic characters in the correct language. 

Regarding the _big_segments_score_, a document receives 0.1 score points for every large segment, up to a maximum score of 1. The length of what we consider a 'large segment' depends on each language and is measured using alphabetic characters. In Spanish, we set the minimum number of alphabetic characters to 250 but in English, for example, the minimum is 232. For more details about language adaptation see the [Adapting subscores to different languages](https://gitlab.prompsit.com/hplt/quality-text-tagger/-/blob/main/README.md#adaptating-subscores-to-different-languages) section.
[MBG] Consider  normalizing this value with the length of the document, in order to avoid penalizing short documents.

On the other hand, the _largest_segments_score_ is used to measure whether a document contains at least one very large segment. The lenght of what we consider a 'very large segment' is also language-dependent. In Spanish, a segment of this kind has between 625 and 1000 alphabetic characters. Depending on the lenght, we assign a value from 0 to 1. If a segment containing 1000 alphabetic characters (or more) is found in a Spanish document, it will receive a score of 1. Likewise, if a document only contains segments with 625 or less alphabetic characters, the resulting _largest_segments_score_ will be 0. If there is more than one of these segments (between both thresholds), we use an average of them.
[MBG] An example of the latter case, plz? You average them but how? the average of lenghts? And then it gets mapped to a value between 0 to 1? 

### urls_score

This score is processed with `crawled_text_qualifier.valorate_urls()`, by looking at the amount of URLs in a document. In particular, we count the amount of "www" or "http" strings in the whole text, and then we get the ratio between the number of URLs and the total amount of segments. We ignore short segments, as for the _language_score_.
The _urls_score_ is language independent, and its value is not lineal. We first get the percentage of URLs per 100 segments:

`number_of_urls / number_of_segments * 100`

Then, a final _urls_score_ is assigned to the document, depending on the percentage of URLs. Documents having more than a 5% of URLs are non-lineally penalized as follows:

| URL score  |    Ratio      |
|---|---|
| 1 | <5 |
| 1 → 0.5 | 5 → 30 |
| 0.5 → 0 | 30 → 100 |
| 0 | >100 |

[MBG] The distribution is lineal in each step?

### numbers_score

This metric is processed with `crawled_text_qualifier.valorate_numbers()`, and it's used to determine whether there is a high number of numeric characters in a document. It is computed by getting the percentage of numeric characters compared to alphabetic characters:

`numeric_characters / alphabetic_characters * 100`

This metric and its thresholds are non-lineal and language-dependent. In Spanish, for example, we assign scores as follows:

| Number score  |    Percentage      |
|---|---|
| 1 | <1 |
| 1 → 0.7 | 1 → 10 |
| 0.7 → 0.5 | 10 → 15 |
| 0.5 → 0 | 15 → 30 |
| 0 | >30 |

[MBG]  Same question as above.

### punctuation_score

The _punctuation_score_ is processed with `crawled_text_qualifier.valorate_punctuation()`. This score is used to penalize texts with too much or too little amount of punctuation characters. The percentage of punctuation characters is calculed this way:

`punctuation_characters / alphabetic_characters * 100`

Again, this metric and its threshold are non-linal and  language-dependent. In Spanish, for example, we give scores according to the following percentages of punctuation characters:

| Punctuation score  |    Percentage      |
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

Note that not only too much punctuation is problematic, but also too few, usually caused by documents that consist of product lists, tags, SEO phrases, etc.

### bad_chars_score

This subscores is processed with `crawled_text_qualifier.valorate_bad_chars()`, and it's used to penalize texts with undesired characters (such as emojis, separators, ...):

`bad_characters / alphabetic_characters * 100`

This score and its thresholds are non-lineal and language-dependent. In Spanish, for example, the score distribution is as follows:

| Bad chars score  |    Percentage      |
|---|---|
| 1 | <1% |
| 1 → 0.7 | 1% → 2% |
| 0.7 → 0.5 | 2% → 6% |
| 0.5 → 0 | 6% → 10% |
| 0 | >10% |

### repeated segments (repeated_score)

The _repeated_score_ score is processed with `crawled_text_qualifier.valorate_repeated()`, and it computes the ratio of repeated segments. Using the same rationale as for the _language_score_ processing, short segments are not taken into account for this metric.  The score follows an inverse function of the amount of repeated segments: for example, 0% of repeated segments will get a 1 score, 20% of repeated segments will have a 0.8 and 100% of repeated segments will receive a 0 score. 

## Adaptating subscores to different languages 

This gets processed in `language_adaptation.extract_ratios()`and `crawled_text_qualifier`.

Some of the subscores used to get the _quality_score_ are based on ratios that need to be computed for each language for optimal performance:
  * _punctuation_score_
  * _bad_chars_score_
  * _numbers_score_
  * _big_segments_score_
  * _largest_segments_score_ 
Also the 'short segments' threshold, indicating the minimum amount of characters that a segment must have in order to being taken into account, is language-dependent.

In our experiments, as a first approach, we stablished the desidered ratios and thresholds for each indicator for the Spanish language, by using a sample  from HPLT v1.2. These ratios are valid for this language only, so an adaptation method is needed for other languages.

In order to adapt the values to other languages, we used the scores and labels provided as metadata in HPLT v1.2. Using a random sample of 10k documents per language, we selected the 50% best language-scored documents ([MBG] Those with most segments in the document language? Plz specify.) and computed ratios for the punctuation, bad characters and numbers subscores. The median for each subscore was computed with `language_adaptation/extract_ratios.py` (GEMA: review this) and then stored in `language_adaptation/medians_language.csv`.Finally, medians are used in the main script (`crawled_text_qualifier.py`) in order to create equivalences between ratios and scores. (GEMA: and this)

Applying the Spanish ratios-score logic to other languages, which can be highly different, produces innacurate _quality_scores_. The histograms below show an example in Korean, where documents that look good got penalized:

![alt text](example/spanish.png)
![alt text](example/korean_non_adapted.png)

[MBG] I'd need to have the info on which were the thresholds in Spanish, so I can understand what gets (wrongly) discarded in Korean. Is it the median?

Aiming at solving this problem, we decided to use medians as a point of reference to more accurately set score ranges. In the example above, Korean has a median of 7.3 in the punctuation score, while Spanish has a median of 2.4. We used this information to make a cross-multiplication in order to get a new and adapted score-ratio relation:

[MBG] I replaced all the mentions to "word characters" to "alphabetic characters", because the other is confusing. If possible, plz change it in the histograms.

![alt text](example/korean_adapted.png)

Using another example, the median of both Russian and Spanish for bad chararcters is the same (0.8), so no adjustments are needed. However, for regular punctuation, ([MBG] What is "regular punctuation"? Has it been mentioned before?) the median is different: 3.2 for Russian and 2.4 in Spanish. In this case, adjustments are indeed needed. The main script uses, again, a cross-multiplication to solve this and set more appropiate values for Russian. If we use the 0.9 ratio (which in Spanish is considered a 1/1 score), it means that Russian needs a 1.2 ratio to get a 1/1 score in the _punctuation_score_:
[MBG] I don't think I get it?
`(3.2 * 0.9) / 2.4 = 1.2`

As a result, the adapted table for Russian regarding the _punctuation_score_ is as follows:

| Punctuation score  |    Ratio Spanish      | Ratio Russian |
|---|---|---|
| 1 | 0.9 → 2.5 | 1.2 → 3.3 |
| __Too much__  |
| 1 → 0.7 | 2.5 → 9 | 3.3 → 12 |
| 0.7 → 0.5 | 9 → 13 | 12 → 17.3 |
| 0.5 → 0 | 13 → 25 | 17.3 → 33.3 |
| 0 | >25 | >33.3 |
| __Too few__  |
| 0 → 0.5 | 0.9 → 0.5 | 1.2 → 0.67 |
| 0.5 → 0 | 0.5 → 0.3 | 0.67 → 0.4 |
| 0 | <0.3 | <0.4 |


Note that not only the relative values are adapted (_punctuation_score_, _bad_chars_score_, _numbers_score_): some absolute values do also  need to be more flexible depending on the language. For example, punctuation ratios are used to adapt the values of _big_segments_score_, _largest_segments_score_ and what we called 'short segments' (the length threshold used to ignore short segments when computing some of the scores). For example, in Spanish we use 1000 alphabetic characters as a threshold for _largest_segments_score_,  with a median of 2.4 in punctuation characters. However, in Japanese, with a median of 6.5, 369 characters are enough, according to the inverse cross-multiplication:

`2.4 * 1000 / 6.5`

The relationship between punctuation and alphabetic characters is inversely proportional: as the number of punctuation symbols per alphabetic characters increases, the average number of alphabetic characters decreases. (GEMA: revisar esto. ) [MBG] I am not sure I am understanding it.

## Glossary
- _document_: whole text of a crawled website
- _segment_: every string grouped between a `\n` character
- _x type character_: see next table

| Name  |  Meaning   |  utf-8 ranges   |
|---|---|---|
|numeric character|Numbers in many languages|0030-0039, 0660-0669, 06F0-06F9, 0964-096F, 09F2-09F9, 0B66-0B77, 0BE6-0BFA, 0C66-0C6F, 0C78-0C7E, 0CE6-0CEF, 0D66-0D79, 0DE6-0DEF, 0E50-0E5B, 0EC0-0ED9, 1040-1049, 1090-1099, 1369-137C, 17E0-17E9, 1810-1819, 19D0-19DA, 1A80-1A99, 1B50-1B59, 1C40-1C49, 1C50-1C59, A830-A839, A8D0-A8D9, AA50-AA59|
|punctuation character|Most frequent linguistic punctuation|0021-0022, 0027-0029, 002C-002E, 003A-003B, 003F, 005B, 005D, 0060, 00A1, 00B4-00B5, 00B7, 00BF,0589-05C7, 0600-061F, 066A-066D, 06D4-06ED, 0700-070F, 1360-1368, 1800-180A, 1AB0-1AFF, 1C78-1C7F, 1CC0-1CC7, 1FBD-1FC1, 1FCD-1FCF, 1FDD-1FDF, 1FED-1FEF, 1FFD-2027, 3000-303F, 4DC0-4DFF, A6F0-A6F7, FE10-FE6F|
|bad character|Non typical linguistic punctuation, emojis, separators, etc.|0023-0026, 002A-002B, 002F, 003C-003E, 0040, 005C, 007C, 007E, 00A2-00B3, 00B8-00BE, 00D7, 00F7, 02B0-0385, 0483-0489, 0559-055F, 2010-2E52, 10000-1FFFF, A670-A67F, 3200-33FF|
|space character|White spaces, tabulations, new lines, etc.|0000-0020, 007F-00A0, 2B7E, 008A, 0088|
|alphabetic character|Characters that are used to create lexical units or words| Any character not in the other groups |

