"""
Usage:
  extract_ratios.py --input=<dir> --output=<dir>

"""


import docopt
import os
import pandas as pd
import re
import json
import sys


args = docopt.docopt(__doc__, version='printbook v 1.0')





## _____ CHARS DETECTION _______________________________________________________________________________________________________________
SINGULAR_CHARS = ["0023-0026", "002A-002B", "002F-002F", "003C-003E", "0040-0040", "005C-005C", "007C-007C", "007E-007E", "00A2-00B3", "00B8-00BE", "00D7-00D7", "00F7-00F7", "02B0-0385", "0483-0489", "0559-055F", "2010-2E52", "10000-1FFFF", "A670-A67F", "3200-33FF"]

PUNCTUATION_CHARS = ["0021-0022", "0027-0029", "002C-002E", "003A-003B", "003F-003F", "005B-005B", "005D-005D", "0060-0060", "00A1-00A1", "00B4-00B5", "00B7-00B7", "00BF-00BF","0589-05C7", "0600-061F", "066A-066D", "06D4-06ED", "0700-070F", "1360-1368", "1800-180A", "1AB0-1AFF", "1C78-1C7F", "1CC0-1CC7", "1FBD-1FC1", "1FCD-1FCF", "1FDD-1FDF", "1FED-1FEF", "1FFD-2027", "3000-303F", "4DC0-4DFF", "A6F0-A6F7", "FE10-FE6F"]

NUMBERS = ["0030-0039", "0660-0669", "06F0-06F9", "0964-096F", "09F2-09F9", "0B66-0B77", "0BE6-0BFA", "0C66-0C6F", "0C78-0C7E", "0CE6-0CEF", "0D66-0D79", "0DE6-0DEF", "0E50-0E5B", "0EC0-0ED9", "1040-1049", "1090-1099", "1369-137C", "17E0-17E9", "1810-1819", "19D0-19DA", "1A80-1A99", "1B50-1B59", "1C40-1C49", "1C50-1C59", "A830-A839", "A8D0-A8D9", "AA50-AA59"]
SPACES = ["0000-0020", "007F-00A0", "2B7E-2B7E", "008A-008A", "0088-0088"]

def join_utf_blocks(u_list, inverse=False):
    inversion = "^" if inverse else ""
    prefixes = ["u", "U000"]
    pattern = f"[{inversion}"
    for x in u_list:
        prefix = prefixes[0] if len(x) == 9 else prefixes[1]
        cases = f'\\{prefix}{x.split("-")[0]}-\\{prefix}{x.split("-")[1]}'
        pattern = f"{pattern}{cases}"
    return re.compile(f"{pattern}]")
    
numbers_pattern = join_utf_blocks(NUMBERS)
singular_chars_pattern = join_utf_blocks(SINGULAR_CHARS)
punctuation_pattern = join_utf_blocks(PUNCTUATION_CHARS)
alpha_pattern = join_utf_blocks(SINGULAR_CHARS + PUNCTUATION_CHARS + NUMBERS + SPACES, inverse=True)
#alphabetic chars are considered by default
spaces_pattern = join_utf_blocks(SPACES)


def score_numbers(word_chars, numbers):
    if word_chars <= 0:
        return 0
    return round((numbers/word_chars)*100, 1)

def score_singular_chars(word_chars, singular_chars):
    if word_chars <= 0:
        return 0
    return round((singular_chars/word_chars)*100, 1)

def score_punctuation(word_chars, punctuation_chars):
    if word_chars <= 0:
        return 0
    return round((punctuation_chars/word_chars)*100, 1)

def score_lang(ref_language, lang_segments, scores_lang, word_chars):
    if len(lang_segments) != len(scores_lang) or len(scores_lang) != len(word_chars):
        #Errors from unmatched scores
        return -1000
    correct_lang_chars = 0
    correct_lang_chars_score = 0
    wrong_lang_chars = 0
    for n in range(len(lang_segments)):
        if word_chars[n] <= 20:
            continue
        elif lang_segments[n] == ref_language:
            correct_lang_chars += word_chars[n]
            correct_lang_chars_score += word_chars[n] * scores_lang[n]
        else:
            wrong_lang_chars += word_chars[n] * scores_lang[n]
    try:
        return round(correct_lang_chars_score / (correct_lang_chars + wrong_lang_chars)*10, 1)
    except:
        return 0



#________________________________________________________________________________________________

input_path=args['--input']
if( not os.path.exists(input_path)):
    print(f"File {input_path} not found")
    sys.exit(-1)

output_path=args['--output']
if( not os.path.exists(output_path)):
    print(f"Directory {output_path} not found")
    sys.exit(-1)
df_medians = pd.DataFrame(columns=["language", "language_score", "numbers_score", "punctuation_score", "singular_chars_score"])
writing_path = os.path.join(output_path, "medians_language.csv")
for json_f in os.listdir(input_path):
    if json_f.endswith(".jsonl"):
        documents = os.path.join(input_path, json_f)
        file_name = os.path.splitext(os.path.basename(json_f))[0]
        df = pd.DataFrame(columns=["language_score", "numbers_ratio", "punctuation_ratio", "singular_chars_ratio"])

        i = 0
        print(f"Processing: {file_name}")
        with open(documents, "r", encoding="utf-8") as file:
            n_lines = sum(1 for _ in file)
            print(f"{file_name} - {n_lines} documents")
        with open(documents, "r", encoding="utf-8") as file:
            for document in file:
                document = json.loads(document)
                condensed_data = [(len(re.findall(alpha_pattern, segment)), len(re.findall(punctuation_pattern, segment)), len(re.findall(singular_chars_pattern, segment)), 
                    len(re.findall(numbers_pattern, segment))) for segment in document["text"].split("\n")]
                word_chars = [x[0] for x in condensed_data]
                punctuation_chars = sum(x[1] for x in condensed_data)
                singular_chars = sum(x[2] for x in condensed_data)
                numbers_chars = sum(x[3] for x in condensed_data)
                
                language_score = score_lang(document["document_lang"], document["langs"], document["scores"], word_chars)
                numbers_score = score_numbers(sum(word_chars), numbers_chars)
                punctuation_score = score_singular_chars(sum(word_chars), punctuation_chars)
                singular_chars_score = score_singular_chars(sum(word_chars), singular_chars)

                df.loc[document["id"]] = [language_score, numbers_score, punctuation_score, singular_chars_score]
                
                i+=1
                if i % 10000 == 0:
                    print(f"{document['document_lang']} - {i}/{n_lines}")
        
        df = df.sort_values(by=["language_score"], ascending=True).iloc[round(df.shape[0]*0.8):]
        df_medians.loc[df_medians.shape[0]] = [document["document_lang"], df.language_score.median(), df.numbers_ratio.median(), df.punctuation_ratio.median(), df.singular_chars_ratio.median()]
df_medians.to_csv(writing_path)
print(f"Saved results in '{writing_path}'")