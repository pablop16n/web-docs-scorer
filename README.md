# Web Docs Scorer

Web Docs Scorer (WDS) is an application that analyzes monolingual documents whose text has been extracted from crawled websites and gives them a score that works as a measure of how good or bad documents are (see below). The score is on a 0 (really bad document) to 10 (very good document) scale, and it is obtained by taking into account textual indicators and metadata. 

Good documents (scores 5-10) are those mainly made of linguistic data, containing large portions of running text distributed across long and well constructed paragraphs. Conversely, bad documents (scores 0-4) are mainly made of non-linguistic characters (like code or emojis) or contain an excess of numbers, puctuation symbols, segment repetitions, etc.  

WDS requires the input documents to be formatted in JSONL, containing the same fields as the documents in the HPLT 1.2 version (see an example of the format [here](https://hplt-project.org/datasets/v1.2)). The current implementation assumes that each document contains information about language identification (at document and segment level), and the text itself with segment boundaries (i.e. `/n`) which (roughly) correspond to paragraphs. 


# Table of contents

1. [How does the WDS work](#how-does-the-WDS-work)
    1. [Computing the _WDS_score_](#computing-the-WDS_score)
    2. [An example of the _WDS_score_](#an-example-of-the-WDS_score)
    3. [Another example of the _WDS_score_](#another-example-of-the-WDS_score)
2. [Usage](#usage)
    1. [docscorer.py (main script)](#docscorerpy-main-script)
    2. [WDS_score_charts.py](#WDS_score_chartspy)
    3. [language_adaption/extract_ratios.py](#language_adaptionextract_ratiospy)
3. [Computing the _penalty_score_](#computing-the-penalty_score)
4. [Computing subscores](#computing-subscores)
    1. [language_score](#language_score)
    2. [long_segments_score and superlong_segments_score](#long_segments_score-and-superlong_segments_score)
    3. [urls_score](#urls_score)
    4. [numbers_score](#numbers_score)
    5. [punctuation_score](#punctuation_score)
    6. [singular_chars_score](#singular_chars_score)
    7. [repeated_score](#repeated-segments-repeated_score)
5. [Adaptating subscores to different languages](#adapting-subscores-to-different-languages)
6. [Glossary](#glossary)

 
## How does the WDS work

In order to give a **_WDS_score_** to a document, the WDS computes several subscores over its content and metadata. Note that higher is always better:

| Subcore  |  Based on   |  Scale   | 
|---|---|---|
| language_score | ratio of [alphabetic characters](#glossary) in the correct language vs. total characters | 0 - 10 | 
| urls_score | ratio of URLs vs. total segments | 0 - 1 | 
| punctuation_score | ratio of [punctuation characters](#glossary) vs. alphabetic characters| 0 - 1 | 
| singular_chars_score | ratio of [singular characters](#glossary) (emojis, non word punctuation, separators, etc.) vs. alphabetic characters | 0 - 1 | 
| numbers_score | ratio of [numeric characters](#glossary) vs. alphabetic characters| 0 - 1 | 
| repeated_score | ratio of repeated segments | 0 - 1 |
| long_segments_score | amount of long segments (alphabetic characters) | 0 - 1 | 
| superlong_segments_score | length of superlong text segments | 0 - 1 | 

All scores are in **rescaled to a 0-10 base in the final outputs**.

A detailed description about these subscores is given in section [Computing subscores](#computing-subscores). 


### Computing the _WDS_score_

The  _WDS_score_ is processed with `docscorer.score_text()`. It combines the aforementioned set of subscores as follows:

1. First, a **_basic_score_** is obtained by adding the subscores that represent positive aspects of the document content: 
  * _language_score_ 
  * _long_segments_score_
  * _superlong_segments_score_

`basic_score = language_score * 0.8 + long_segments_score + superlong_segments_score`

Note that the _language_score_ is weighted (since it scores from 0 to 10, while the other values score 0 to 1), so the maximum possible value of the _basic_score_ is 10.

2. Then, we use the rest of the subscores (which represent negative aspects of the document content) to compute a **_penalty_score_**:
  * _urls_score_
  * _numbers_score_
  * _punctuation_score_
  * _singular_chars_score_
  * _repeated_score_

`penalty_score = first_lowest_negative_subscore_value * second_lowest_negative_subscore_value * average (remaining_negative_subscores_values) `

`first_lowest_negative_subscore_value` and `second_lowest_negative_subscore_value` are the two subscores with the lowest values. Thus, a 0 value in any of the negative scores will suppose a 0 score in the final _WDS_score_ regardless the other scores.  Please, see section [Computing the _penalty_score_](#computing-the-penalty_score) for more details.

3. Finally, we get the final **_WDS_score_** by multipliying the **_basic_score_** by the **_penalty_score_**. Note that _penalty_score_ is always 0-1:

`WDS score = basic score * penalty score`


### An example of the _WDS_score_

In this section we show an example on how the **_WDS_score_** is computed, and the meaning of its subscores. The document is extracted from the HPLT v1.2 Italian dataset, and can be found in `example/ita_Latn.jsonl`. An excerpt of the document is shown below:

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
| url_score | 1.0 |
| punctuation_score | 1.0 |
| singular_chars_score | 1.0 |
| numbers_score | 0.92 |
| repeated_score | 0.96 |
| long_segments_score | 0.4 |
| superlong_segments_score | 1.0 |

As explained in the section above, the **_WDS_score_** of the document is computed by using these subscores values:

**basic score** = (9.9 x 0.8) + 0.4 + 1 = **9.32**

**penalty score** = 0.92 x 0.96 x ((1+1+1)/3) =  **0.88**

**WDS score** = 9.32 x 0,88 = **8.2** 

This means that the previous example is a good document (**_WDS_score_** = 8.2/10), that is clearly in Italian (_language_score_ = 9.9/10). It probably contains a considerable amount of textual data in some segments (_superlong_segment_score_ = 1/1), because there is almost one 'very long segment', but it only contains 4 'long segments' (_long_segments_score_ = 0.4/1). For Italian we consider 'superlong segments' those with more than 1208 alphabetic characters and to be considered a 'long segment' almost 302 alphabetic characters are needed. For more information about these scores see the [long_segments_score and superlong_segments_score](#adapting-subscores-to-different-languages) sections.

The document does not contain enough URLs, punctuation or singular characters noise to be penalized because of it (_url_score_ = 1/1, _punctuation_score_ = 1/1, _singular_chars_score_ = 1/1). It contains a small excess of numbers (_numbers_score_ = 0.92/1), which could be due to the presence of a calendar present in the text:

> [...] _Gennaio 2022 Giugno 2021 \n Marzo 2021 \n Novembre 2020 \n Ottobre 2020..._ [...]

The document also has some repeated segments (_repeated_score_ = 0.96/1) caused by recurrent headers or titles:

>[...] Grammatica, livello avanzato [...]
> Grammatica, livello avanzato [...]


### Another example of the _WDS_score_

The following excerpt belongs to the file `example/example2.txt`, a bad scored Chinese document from the HPLT v1.2 dataset. The document got a **_WDS_score_** of 1.5:

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
| url_score | 0.44 |
| punctuation_score | 0.9 |
| singular_chars_score | 1 |
| numbers_score | 0.56 |
| repeated_score | 1 |
| long_segments_score | 0.1 |
| superlong_segments_score | 0.0 |

This text seems to be mostly made of short segments (note the very low values for _long_segments_score_ and _superlong_segments_score_) and, according to the language identifier, with a part of the segments not in the document language. Because of this, the basic score is already low: 

|basic score| Result |
|---|---|
|8 * 0.8 + 0.1 + 0| 6.5 |


The document does not seem to have bad punctuation or too many singular characters, and it does not contain repeated sentences. However, it has an excess of numeric characters and URLs. This has a high impact on the _penalty_score_ value:

|penalty score| Result |
|---|---|
|0.44 * 0.56 * 0.97| 0.24 |

Thus, the final _WDS_score_ is also very low:

|basic score * penalty score| Result |
|---|---|
| 6.5 * 0.24| 1.5 |

With such a low WDS score, this document can be considered an undesirable document. 

## Usage


### docscorer.py

The main script, it will create a csv for each jsonl present in the input directory. The input jsonl files should be named as shown in this example `ell_Grek.jsonl`, thus the entire file names should follow the convention of using the three-letter language code (ISO 639-3) and the four-letter script code (ISO 15924) separated by an underscore. These files must contain the next columns:
- `id`: identifier of the document, must be unique.
- `scores`: list of language probability scores from the language identifier (list of integer or float numbers, must be correlated with _langs_ field).
- `langs`: list of language labels for each segment of the document (list of ISO 639-3 language codes, must be correlated with _scores_ field).
- `text`: text of the document. Segments must be separated by _\n_.

The output csvs will contain the next columns. The final score will always be considered the _WDS_score_:
- WDS_score
- language_score
- url_score
- punctuation_score
- singular_chars_score
- numbers_score
- repeated_score
- n_long_segments_score
- superlong_segment_score

#### Parameters
- ```input```: directory with jsonl files provided by the language identifier
- ```output```: existing directory (optional)
- ```config```: path of the `medians_language.csv` document (optional)

#### Example

```python3 docscorer.py --input=input_dir --output=output_dir --config=language_adaption/medians_language.csv ```


#### Requirements
The document `./language_adaption/medians_language.csv` created by `./language_adaption/extract_ratios.py` is needed. It can be used the csv present by default in the repository or it can be created with custom data. These data is used as a model to undestand the differences between languages, so in a custom approach the text data used must be representative, diverse and comparable.

### WDS_charts.py

Script that creates a HTML document with one histogram for every csv document in the input.

#### Parameters 
- ```input```: directory with the csvs obtained with `docscorer.py`
- ```output```: existing directory

#### Example

```python3 WDS_charts.py --input=input_dir --output=output_dir ```

#### Requirements

It is needed a directory with the `docscorer.py` output.

#### language_adaption/extract_ratios.py

This script extracts the median ratios of numbers, punctuation and singular characters which are used to process the language adaption from a sample of documents. The input data must consists in a jsonl file for every language with the structure of HPLT 1.2v. The selected data must be representative, diverse and comparable.

#### Parameters 
- ```input```: directory with jsonl files they must have the HPLT 1.2v like structure regarding keys and values.
- ```output```: existing directory

#### Example

```python3 extract_ratios.py --input=input_dir --output=output_dir ```

## Computing the _penalty_score_

The _penalty_score_  is obtained with `docscorer.custom_mean()` . The subscores used to compute the **_penalty_score_** are those that represent the negative aspects of the document:
  *  _urls_score_
  * _numbers_score_
  * _punctuation_score_
  * _singular_chars_score_
  * _repeated_score_

The _penalty_score_ ranges on a scale from 0 (the document is severely penalized and gets a final _WDS_score_ of 0) to 1 (no penalization is applied).

To compute the _penalty_score_, the two lowest values from the aforementioned subsscores are multiplied by the average of the rest of values:

`first_lowest_value * second_lowest_value * average(other_values)`

We prefer this solution to a simple average because the aim of these scores is to warn about documents that stand out of the desired ratios: a simple average would overshadow low values (which are the most valuable to our goal), while a simple multiplication of all scores would make it hard to work with more than 4 or 5 penalty variables.


## Computing subscores

### language_score

The _language_score_ is processed with `docscorer.score_lang()`. It uses the information about language identification at segment and document level (provided as metadata in the input files) in order to get the ratio of [alphabetic characters](#glossary) in the correct language. Segments whose language matches the document language are considered correct and segments with a different language are considered wrong. The application assumes that the text inside the document is always written with the language script indicated in the [file name](#docscorerpy-main-script). The _language_score_ is a value that ranges from 0 (worst score) to 10 (best score), and is computed as follows:

`correct_characters / (correct_characters + wrong_characters) * 10`

Segments below a certain length threshold are not taken into account to this metric, so this score is not sensitive to short segments (which often  to header or footer menus, social media listings, partners listings, etc.) These strings are troublesome for language identifiers as they are usually classified as English or other random language. The length threshold is different for each language. For example, 25 is considered the minimum acceptable number of characters for taking Spanish segments into account for this metric.

### long_segments_score and superlong_segments_score

These two metrics are obtained with `docscorer.score_long_texts()`.  They get values between 0 and 1 that aim at determining the presence of large groups of alphabetic characters in the correct language. 

Regarding the _long_segments_score_, a document receives 0.1 score points for every long segment, up to a maximum score of 1. The length of what we consider a 'long segment' depends on each language and is measured using alphabetic characters. In Spanish, we set the minimum number of alphabetic characters to 250 but in English, for example, the minimum is 232. For more details about language adaption see the [Adapting subscores to different languages](#adapting-subscores-to-different-languages) section.
<!-- [MBG] Consider  normalizing this value with the length of the document, in order to avoid penalizing short documents. -->

On the other hand, the _superlong_segments_score_ is used to measure whether a document contains at least one very long segment. The lenght of what we consider a 'very long segment' is also language-dependent. In Spanish, a segment of this kind has between 625 and 1000 alphabetic characters. Depending on the lenght, we assign a value from 0 to 1. If a segment containing 1000 alphabetic characters (or more) is found in a Spanish document, it will receive a score of 1. Likewise, if a document only contains segments with 625 or less alphabetic characters, the resulting _superlong_segments_score_ will be 0. If there is more than one of these segments (inside both thresholds), we use an average of their lengths to calculate the value.

### urls_score

This score is processed with `docscorer.score_urls()`, by looking at the amount of URLs in a document. In particular, we count the amount of "www" or "http" strings in the whole text, and then we get the ratio between the number of URLs and the total amount of segments. We ignore short segments, as for the _language_score_.
The _urls_score_ is language independent, and its value is not lineal. We first get the percentage of URLs per 100 segments:

`number_of_urls / number_of_segments * 100`

Then, a final _urls_score_ is assigned to the document, depending on the percentage of URLs. Documents having more than a 5% of URLs are lineally penalized as follows:

| URL score  |    Ratio      |
|---|---|
| 1 | <5 |
| 1 → 0.5 | 5 → 30 |
| 0.5 → 0 | 30 → 100 |
| 0 | >100 |

### numbers_score

This metric is processed with `docscorer.score_numbers()`, and it's used to determine whether there is a high number of numeric characters in a document. It is computed by getting the percentage of numeric characters compared to alphabetic characters:

`numeric_characters / alphabetic_characters * 100`

This metric and its thresholds are lineal and language-dependent. In Spanish, for example, we assign scores as follows:

| Number score  |    Percentage      |
|---|---|
| 1 | <1 |
| 1 → 0.7 | 1 → 10 |
| 0.7 → 0.5 | 10 → 15 |
| 0.5 → 0 | 15 → 30 |
| 0 | >30 |

### punctuation_score

The _punctuation_score_ is processed with `docscorer.score_punctuation()`. This score is used to penalize texts with too much or too little amount of punctuation characters. The percentage of punctuation characters is calculed this way:

`punctuation_characters / alphabetic_characters * 100`

Again, this metric and its threshold are lineal and  language-dependent. In Spanish, for example, we give scores according to the following percentages of punctuation characters:

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

### singular_chars_score

This subscores is processed with `docscorer.score_singular_chars()`, and it's used to penalize texts with undesired characters (such as emojis, separators, ...):

`singular_characters / alphabetic_characters * 100`

This score and its thresholds are lineal and language-dependent. In Spanish, for example, the score distribution is as follows:

| Singular chars score  |    Percentage      |
|---|---|
| 1 | <1% |
| 1 → 0.7 | 1% → 2% |
| 0.7 → 0.5 | 2% → 6% |
| 0.5 → 0 | 6% → 10% |
| 0 | >10% |

### repeated segments (repeated_score)

The _repeated_score_ score is processed with `doscorer.score_repeated()`, and it computes the ratio of repeated segments. Using the same rationale as for the _language_score_ processing, short segments are not taken into account for this metric.  The score follows an inverse function of the amount of repeated segments: for example, 0% of repeated segments will get a 1 score, 20% of repeated segments will have a 0.8 and 100% of repeated segments will receive a 0 score. 

## Adaptating subscores to different languages 

This gets processed in `language_adaption.extract_ratios()` and `docscorer`.

Some of the subscores used to get the _WDS_score_ are based on ratios that need to be computed for each language for optimal performance:
  * _punctuation_score_
  * _singular_chars_score_
  * _numbers_score_
  * _long_segments_score_
  * _very_long_segments_score_ 
Also the 'short segments' threshold, indicating the minimum amount of characters that a segment must have in order to being taken into account, is language-dependent.

In our experiments, as a first approach, we stablished the desidered ratios and thresholds for each indicator for the Spanish language, by using a sample  from HPLT v1.2. These ratios are valid for this language only, so an adaption method is needed for other languages.

In order to adapt the values to other languages, we used the scores and labels provided as metadata in HPLT v1.2. from a sample of 10k documents per language. Every document was analized with a modified version of the [_language_score_](#language_score). In the modified version, the number of correct alphabetic characters of every segment is multiplied by the language identifier probability of the segment. We want to know which documents have the highest proportion of segments and the better probability in the correct language. For example, let us consider a document with three segments, the first one has a language probability of 0.9 and contains 500 alphabetic characters. The second has a low language probability (0.4) and 25 alphabetic characters. The third is not in the correct language and contains only 10 alphabetic characters. The calculation of the modified _language_score_ will be:

```
sum(correct_word_characters * language_probability) / sum(correct_word_characters + wrong_word_characters) * 10

(500 * 0.9 + 25 * 0.4) / (500 + 25 + 10) * 10 = 8.6
```

Using these random samples of 10k documents, we selected the 50% best scored documents to extract their ratios for punctuation, singular characters and numbers. The medians of ratios, that we will need for each subscore, were computed with `language_adaption/extract_ratios.py` and then stored in `language_adaption/medians_language.csv`. Finally, these medians are used in the main script (`docscorer.py`) in order to adapt ratios to every language.

Applying the Spanish ratio-score equivalences to other languages, which can be highly different, produces innacurate _WDS_scores_. The histograms below show an example in Korean, where documents that look good got penalized. The samples in the pictures are processed with the same ratio-score equivalences that we showed in the table of [_punctuation_score_](#punctuation_score):

![alt text](example/spanish.png)
![alt text](example/korean_non_adapted.png)

Aiming at solving this problem, we decided to use medians as a point of reference to more accurately set score ranges. In the example above, Korean has a median of 7.3 in the punctuation score, while Spanish has a median of 2.4. We used this information to make a cross-multiplication in order to get a new and adapted score-ratio relation:

![alt text](example/korean_adapted.png)

Using another example, the median of both Russian and Spanish for singular characters is the same (0.8), so no adjustments are needed. However, for punctuation, the median is different: 3.2 for Russian and 2.4 in Spanish. In this case, adjustments are indeed needed. The main script uses, again, a cross-multiplication to solve this and set more appropiate values for Russian. If we consider the _punctuation_score_ table (see table below), in Spanish a ratio between **0.9** and **2.5** is mandatory to get a perfect document (_punctuation_score_ = 1). With the cross-multiplication conversion, we can fit a better benchmark for non penalized documents:

`(3.2 * 0.9) / 2.4 = 1.2`

`(3.2 * 2.5) / 2.4 = 3.3`

As a result, the adapted table for Russian regarding the _punctuation_score_ is as follows:

| Punctuation score  |    Ratio Spanish      | Ratio Russian |
|---|---|---|
| 1 | **0.9** → 2.5 | 1.2 → 3.3 |
| __Too much__  |
| 1 → 0.7 | 2.5 → 9 | 3.3 → 12 |
| 0.7 → 0.5 | 9 → 13 | 12 → 17.3 |
| 0.5 → 0 | 13 → 25 | 17.3 → 33.3 |
| 0 | >25 | >33.3 |
| __Too few__  |
| 0 → 0.5 | 0.9 → 0.5 | 1.2 → 0.67 |
| 0.5 → 0 | 0.5 → 0.3 | 0.67 → 0.4 |
| 0 | <0.3 | <0.4 |


Note that not only the relative values are adapted (_punctuation_score_, _singular_chars_score_, _numbers_score_): some absolute values do also  need to be more flexible depending on the language. For example, punctuation ratios are used to adapt the values of _long_segments_score_, _superlong_segments_score_ and what we called 'short segments' (the length threshold used to ignore short segments when computing some of the scores). For example, in Spanish we use 1000 alphabetic characters as a threshold for _superlong_segments_score_,  with a median of 2.4 in punctuation characters. However, in Japanese, with a median of 6.5, 369 characters are enough, according to the inverse cross-multiplication:

`2.4 * 1000 / 6.5`

The inverse cross-multiplication is used because the relationship between punctuation and alphabetic characters is inversely proportional. A language that normally uses less alphabetic characters than other will have a bigger ratio of punctuation. For example, in our test sample, German has a punctuation ratio of 2.8, this means that every punctuation mark usually needs 36 alphabetic characters (100/2.8 ≈ 36). In Chinese we found a ratio of 9.9, 10 alphabetic characters are thus needed every 10 alphabetic characters. We use the punctuation as a point of reference to extract the average alphabetic characters of the language, so we can obtain the conversion of what we called long or superlong segments.

In case the analysed language is not present in `configurations/language_adaption/medians_language.csv`, we use the data of the [WALS](https://wals.info/) to find the closest related languages (within the same script system). The application uses the average of these data to fit the parameters. If it occurs that is not possible to find a related language, the average ratio of all other languages is used.

## Glossary
- _document_: whole text of a crawled website
- _segment_: every string grouped between a `\n` character
- _x type character_: see next table

| Name  |  Meaning   |  utf-8 ranges   |
|---|---|---|
|numeric character|Numbers in many languages|0030-0039, 0660-0669, 06F0-06F9, 0964-096F, 09F2-09F9, 0B66-0B77, 0BE6-0BFA, 0C66-0C6F, 0C78-0C7E, 0CE6-0CEF, 0D66-0D79, 0DE6-0DEF, 0E50-0E5B, 0EC0-0ED9, 1040-1049, 1090-1099, 1369-137C, 17E0-17E9, 1810-1819, 19D0-19DA, 1A80-1A99, 1B50-1B59, 1C40-1C49, 1C50-1C59, A830-A839, A8D0-A8D9, AA50-AA59|
|punctuation character|Most frequent linguistic punctuation|0021-0022, 0027-0029, 002C-002E, 003A-003B, 003F, 005B, 005D, 0060, 00A1, 00B4-00B5, 00B7, 00BF,0589-05C7, 0600-061F, 066A-066D, 06D4-06ED, 0700-070F, 1360-1368, 1800-180A, 1AB0-1AFF, 1C78-1C7F, 1CC0-1CC7, 1FBD-1FC1, 1FCD-1FCF, 1FDD-1FDF, 1FED-1FEF, 1FFD-2027, 3000-303F, 4DC0-4DFF, A6F0-A6F7, FE10-FE6F|
|singular character|Non typical linguistic punctuation, emojis, separators, etc.|0023-0026, 002A-002B, 002F, 003C-003E, 0040, 005C, 007C, 007E, 00A2-00B3, 00B8-00BE, 00D7, 00F7, 02B0-0385, 0483-0489, 0559-055F, 2010-2E52, 10000-1FFFF, A670-A67F, 3200-33FF|
|space character|White spaces, tabulations, new lines, etc.|0000-0020, 007F-00A0, 2B7E, 008A, 0088|
|alphabetic character|Characters that are used to create lexical units or words| Any character not in the other groups |

