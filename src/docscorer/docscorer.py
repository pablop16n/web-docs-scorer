"""
Usage:
  docscorer.py lang --input=<dir> [--output=<dir>] [--config=<csv>]

"""

import logging
import docopt
import os
import pandas as pd
import re
import json
import sys

try:
    from .utils import average, precision_round, join_utf_blocks, custom_mean
except ImportError:
    from utils import average, precision_round, join_utf_blocks, custom_mean



class DocumentScorer:
    def __init__(self, target_language,   config=os.path.dirname(__file__)+"/language_adaption/medians_language.csv"):
    ## _____ LANGUAGE ADAPTATION DATA ________________________________________________________________________________________________
        df_lang_adaption = pd.read_csv(config)
        
        if len(target_language)==2:
            df_lang_adaption.set_index("language", inplace=True)
            ref_langcode="es"
        else:
            df_lang_adaption.set_index("language_3", inplace=True)
            ref_langcode="spa"

        LANGUAGES = df_lang_adaption.index       
        
        self.ref_language = target_language

        ## _____ REFERENCE RATIO VALUES FOR SPANISH ________________________________________________________________________________________________
        #Current values in the provided csv 
        #Menu
        menu_length = 25

        #Punctuation
        punct_max = 25
        punct_bad = [13, 0.5]
        punct_semibad = [9, 0.3]
        punct_desired_max = 2.5
        punct_desired_min = 0.9

        #Singular chars
        singular_chars_max = 10
        singular_chars_bad = 6
        singular_chars_semibad = 2
        singular_chars_desired =  1
        
        #Numbers
        numbers_max = 30
        numbers_bad = 15
        numbers_semibad = 10
        numbers_desired = 1 

        #Long text
        long_text_min = 250
        long_text_max = 1000

        ref_numbers = round(df_lang_adaption.loc[ref_langcode]["numbers_score"], 1) 
        ref_punctuation = round(df_lang_adaption.loc[ref_langcode]["punctuation_score"], 1)
        ref_singular_chars = round(df_lang_adaption.loc[ref_langcode]["singular_chars_score"], 1)
    
        if target_language in LANGUAGES:
            LANGUAGES_NUMBERS = round(df_lang_adaption.loc[target_language]["numbers_score"], 1)
            LANGUAGES_PUNCTUATION = round(df_lang_adaption.loc[target_language]["punctuation_score"], 1) 
            LANGUAGES_SINGULAR_CHARS = round(df_lang_adaption.loc[target_language]["singular_chars_score"], 1)
    
            ## MENUS ADAPTION
            self.MENUS_AVERAGE_LENGTH = round(ref_punctuation * menu_length / LANGUAGES_PUNCTUATION)
            #PUNCTUATION SCORING
            self.PUNCTUATION_PERCENT_MAX = round(LANGUAGES_PUNCTUATION * punct_max / ref_punctuation,1) if LANGUAGES_PUNCTUATION * punct_max / ref_punctuation < 100 else 100.0
            self.PUNCTUATION_PERCENT_BAD = round(LANGUAGES_PUNCTUATION * punct_bad[0] / ref_punctuation,1), round(LANGUAGES_PUNCTUATION * punct_bad[1] / ref_punctuation, 1)
            self.PUNCTUATION_PERCENT_SEMIBAD = round(LANGUAGES_PUNCTUATION * punct_semibad[0] / ref_punctuation,1), round(LANGUAGES_PUNCTUATION * punct_semibad[1] / ref_punctuation, 1)
            self.PUNCTUATION_PERCENT_DESIRED_MAX = round(LANGUAGES_PUNCTUATION * punct_desired_max / ref_punctuation,1)
            self.PUNCTUATION_PERCENT_DESIRED_MIN = round(LANGUAGES_PUNCTUATION * punct_desired_min / ref_punctuation,1)
            ## _____ SINGULAR CHARS SCORING _______________________________________________________________________________________________________________
            self.SINGULAR_CHARS_PERCENT_MAX = round(LANGUAGES_SINGULAR_CHARS * singular_chars_max / ref_singular_chars,1) if LANGUAGES_SINGULAR_CHARS * singular_chars_max / ref_singular_chars < 100 else 100.0
            self.SINGULAR_CHARS_PERCENT_BAD = round(LANGUAGES_SINGULAR_CHARS * singular_chars_bad / ref_singular_chars,1)
            self.SINGULAR_CHARS_PERCENT_SEMIBAD = round(LANGUAGES_SINGULAR_CHARS * singular_chars_semibad / ref_singular_chars,1)
            self.SINGULAR_CHARS_PERCENT_DESIRED = round(LANGUAGES_SINGULAR_CHARS * singular_chars_desired / ref_singular_chars,1)
            ## _____ NUMBERS SCORING _______________________________________________________________________________________________________________
            self.NUMBERS_PERCENT_MAX = round(LANGUAGES_NUMBERS * numbers_max / ref_numbers,1) if LANGUAGES_NUMBERS * numbers_max / ref_numbers < 100 else 100.0
            self.NUMBERS_PERCENT_BAD = round(LANGUAGES_NUMBERS * numbers_bad / ref_numbers,1) if LANGUAGES_NUMBERS * numbers_max / ref_numbers < 100 else 100.0
            self.NUMBERS_PERCENT_SEMIBAD = round(LANGUAGES_NUMBERS * numbers_semibad / ref_numbers,1)
            self.NUMBERS_PERCENT_DESIRED = round(LANGUAGES_NUMBERS * numbers_desired / ref_numbers,1)    
            ## _____ LONG SEGMENTS SCORING _______________________________________________________________________________________________________________
            self.LONG_TEXT_MAX = round(ref_punctuation * long_text_max / LANGUAGES_PUNCTUATION)
            self.LONG_TEXT_MIN = round(ref_punctuation * long_text_min / LANGUAGES_PUNCTUATION)

            
        else:
            #if the language is not in the config CSV, an average of all language is used            
            LANGUAGES_NUMBERS_ALL = {lang : round(df_lang_adaption.loc[lang]["numbers_score"], 1) for lang in LANGUAGES}
            LANGUAGES_PUNCTUATION_ALL = {lang : round(df_lang_adaption.loc[lang]["punctuation_score"], 1) for lang in LANGUAGES}
            LANGUAGES_SINGULAR_CHARS_ALL = {lang : round(df_lang_adaption.loc[lang]["singular_chars_score"], 1) for lang in LANGUAGES}
        
            ## _____ MENUS ADAPTION _______________________________________________________________________________________________________________
            MENUS_AVERAGE_LENGTH_ALL = {lang: round(ref_punctuation * menu_length / val) for lang, val in LANGUAGES_PUNCTUATION_ALL.items()}
            self.MENUS_AVERAGE_LENGTH = average(MENUS_AVERAGE_LENGTH_ALL.values())        
            
            ## _____ PUNCTUATION SCORING _______________________________________________________________________________________________________________
            PUNCTUATION_PERCENT_MAX_ALL = {lang: round(val * punct_max / ref_punctuation,1) if val * punct_max / ref_punctuation < 100 else 100.0 for lang, val in LANGUAGES_PUNCTUATION_ALL.items()}
            self.PUNCTUATION_PERCENT_MAX = average(PUNCTUATION_PERCENT_MAX_ALL.values())

            PUNCTUATION_PERCENT_BAD_ALL = {lang: (round(val * punct_bad[0] / ref_punctuation,1), round(val * punct_bad[1] / ref_punctuation, 1)) for lang, val in LANGUAGES_PUNCTUATION_ALL.items()}
            self.PUNCTUATION_PERCENT_BAD = (average([x[0] for x in PUNCTUATION_PERCENT_BAD_ALL.values()]), average([x[1] for x in PUNCTUATION_PERCENT_BAD_ALL.values()]))

            PUNCTUATION_PERCENT_SEMIBAD_ALL = {lang: (round(val * punct_semibad[0] / ref_punctuation,1), round(val * punct_semibad[1] / ref_punctuation, 1)) for lang, val in LANGUAGES_PUNCTUATION_ALL.items()}
            self.PUNCTUATION_PERCENT_SEMIBAD = (average([x[0] for x in PUNCTUATION_PERCENT_SEMIBAD_ALL.values()]), average([x[1] for x in PUNCTUATION_PERCENT_SEMIBAD_ALL.values()]))

            PUNCTUATION_PERCENT_DESIRED_MAX_ALL = {lang: round(val * punct_desired_max / ref_punctuation,1) for lang, val in LANGUAGES_PUNCTUATION_ALL.items()}
            self.PUNCTUATION_PERCENT_DESIRED_MAX = average(PUNCTUATION_PERCENT_DESIRED_MAX_ALL.values())

            PUNCTUATION_PERCENT_DESIRED_MIN_ALL  = {lang: round(val * punct_desired_min / ref_punctuation,1) for lang, val in LANGUAGES_PUNCTUATION_ALL.items()}
            self.PUNCTUATION_PERCENT_DESIRED_MIN = average(PUNCTUATION_PERCENT_DESIRED_MIN_ALL.values())
            
            ## _____ SINGULAR CHARS SCORING _______________________________________________________________________________________________________________
            SINGULAR_CHARS_PERCENT_MAX_ALL = {lang: round(val * singular_chars_max / ref_singular_chars,1) if val * singular_chars_max / ref_singular_chars < 100 else 100.0 for lang, val in LANGUAGES_SINGULAR_CHARS_ALL.items()}
            self.SINGULAR_CHARS_PERCENT_MAX = average(SINGULAR_CHARS_PERCENT_MAX_ALL.values())

            SINGULAR_CHARS_PERCENT_BAD_ALL = {lang: round(val * singular_chars_bad / ref_singular_chars,1) for lang, val in LANGUAGES_SINGULAR_CHARS_ALL.items()}
            self.SINGULAR_CHARS_PERCENT_BAD = average(SINGULAR_CHARS_PERCENT_BAD_ALL.values())

            SINGULAR_CHARS_PERCENT_SEMIBAD_ALL = {lang: round(val * singular_chars_semibad / ref_singular_chars,1) for lang, val in LANGUAGES_SINGULAR_CHARS_ALL.items()}
            self.SINGULAR_CHARS_PERCENT_SEMIBAD = average(SINGULAR_CHARS_PERCENT_SEMIBAD_ALL.values())

            SINGULAR_CHARS_PERCENT_DESIRED_ALL  = {lang: round(val * singular_chars_desired / ref_singular_chars,1) for lang, val in LANGUAGES_SINGULAR_CHARS_ALL.items()}
            self.SINGULAR_CHARS_PERCENT_DESIRED = average(SINGULAR_CHARS_PERCENT_DESIRED_ALL.values())
        
            ## _____ NUMBERS SCORING _______________________________________________________________________________________________________________
            NUMBERS_PERCENT_MAX_ALL = {lang: round(val * numbers_max / ref_numbers,1) if val * numbers_max / ref_numbers < 100 else 100.0 for lang, val in LANGUAGES_NUMBERS_ALL.items()}
            self.NUMBERS_PERCENT_MAX = average(NUMBERS_PERCENT_MAX_ALL.values())

            NUMBERS_PERCENT_BAD_ALL = {lang: round(val * numbers_bad / ref_numbers,1) if val * numbers_max / ref_numbers < 100 else 100.0 for lang, val in LANGUAGES_NUMBERS_ALL.items()}
            self.NUMBERS_PERCENT_BAD = average(NUMBERS_PERCENT_BAD_ALL.values())

            NUMBERS_PERCENT_SEMIBAD_ALL = {lang: round(val * numbers_semibad / ref_numbers,1) for lang, val in LANGUAGES_NUMBERS_ALL.items()}
            self.NUMBERS_PERCENT_SEMIBAD = average(NUMBERS_PERCENT_SEMIBAD_ALL.values())

            NUMBERS_PERCENT_DESIRED_ALL = {lang: round(val * numbers_desired / ref_numbers,1) for lang, val in LANGUAGES_NUMBERS_ALL.items()}
            self.NUMBERS_PERCENT_DESIRED = average(NUMBERS_PERCENT_DESIRED_ALL.values())

            ## _____ LONG SEGMENTS SCORING _______________________________________________________________________________________________________________
            LONG_TEXT_MAX_ALL = {lang: round(ref_punctuation * long_text_max / val) for lang, val in LANGUAGES_PUNCTUATION_ALL.items()}
            self.LONG_TEXT_MAX = average(LONG_TEXT_MAX_ALL.values())

            LONG_TEXT_MIN_ALL = {lang: round(ref_punctuation * long_text_min / val) for lang, val in LANGUAGES_PUNCTUATION_ALL.items()}
            self.LONG_TEXT_MIN = average(LONG_TEXT_MIN_ALL.values())

        #COMMON VALUES:

        # Number of long texts that means a 10 score
        self.DESIRED_LONG_TEXTS = 10
        
        ## _____ CHARS DETECTION _______________________________________________________________________________________________________________
        # Regex unicode codes for char-type count
        SINGULAR_CHARS = ["0023-0026", "002A-002B", "002F-002F", "003C-003E", "0040-0040", "005C-005C", "007C-007C", "007E-007E", "00A2-00B3", "00B8-00BE", "00D7-00D7", "00F7-00F7", "02B0-0385", "0483-0489", "0559-055F", "2010-2E52", "10000-1FFFF", "A670-A67F", "3200-33FF"]
        PUNCTUATION_CHARS = ["0021-0022", "0027-0029", "002C-002E", "003A-003B", "003F-003F", "005B-005B", "005D-005D", "0060-0060", "00A1-00A1", "00B4-00B5", "00B7-00B7", "00BF-00BF","0589-05C7", "0600-061F", "066A-066D", "06D4-06ED", "0700-070F", "1360-1368", "1800-180A", "1AB0-1AFF", "1C78-1C7F", "1CC0-1CC7", "1FBD-1FC1", "1FCD-1FCF", "1FDD-1FDF", "1FED-1FEF", "1FFD-2027", "3000-303F", "4DC0-4DFF", "A6F0-A6F7", "FE10-FE6F"]
        NUMBERS = ["0030-0039", "0660-0669", "06F0-06F9", "0964-096F", "09F2-09F9", "0B66-0B77", "0BE6-0BFA", "0C66-0C6F", "0C78-0C7E", "0CE6-0CEF", "0D66-0D79", "0DE6-0DEF", "0E50-0E5B", "0EC0-0ED9", "1040-1049", "1090-1099", "1369-137C", "17E0-17E9", "1810-1819", "19D0-19DA", "1A80-1A99", "1B50-1B59", "1C40-1C49", "1C50-1C59", "A830-A839", "A8D0-A8D9", "AA50-AA59"]
        SPACES = ["0000-0020", "007F-00A0", "2B7E-2B7E", "008A-008A", "0088-0088"]

        self.numbers_pattern = join_utf_blocks(NUMBERS)
        self.singular_chars_pattern = join_utf_blocks(SINGULAR_CHARS)
        self.punctuation_pattern = join_utf_blocks(PUNCTUATION_CHARS)
        self.word_pattern = join_utf_blocks(SINGULAR_CHARS + PUNCTUATION_CHARS + NUMBERS + SPACES, inverse=True) #alphabetic chars are considered by default
        # self.spaces_pattern = join_utf_blocks(SPACES)


## _____SCORING FUNCTIONS _______________________________________________________________________________________________________________
    def __score_lang(self, lang_segments, scores_lang, word_chars):
        if len(lang_segments) != len(scores_lang) or len(scores_lang) != len(word_chars):
            return 10 #Errors from unmatched scores
        correct_lang_chars = 0
        wrong_lang_chars = 0
        for n in range(len(lang_segments)):
            if word_chars[n] <= self.MENUS_AVERAGE_LENGTH:
                continue
            elif lang_segments[n].split("_")[0] == self.ref_language:
                correct_lang_chars += word_chars[n]
            elif scores_lang[n] > 0.2:
                wrong_lang_chars += word_chars[n]
                
        if correct_lang_chars == 0:
            return 0
        results = (correct_lang_chars / (correct_lang_chars + wrong_lang_chars)*10)
        return round(results, 1) if results <= 10 else 10


    def __score_urls(self, document, word_chars):
        n_segments = len([x for x in word_chars if x > self.MENUS_AVERAGE_LENGTH])
        if n_segments == 0:
            return 10
    
        url_quantity = max([document.count("www"), document.count("http")])
        url_quantity = url_quantity/n_segments
    
        if url_quantity <= 0.05:
            return 10
        elif url_quantity >= 1:
            return 0
        elif url_quantity > 0.3:
            min_value = 1
            max_value = 0.3
            min_range = 0
            max_range = 5
        else:
            min_value = 0.3
            max_value = 0.05
            min_range = 5
            max_range = 10
            
        return round(((url_quantity - min_value) / (max_value - min_value) * (max_range - min_range) + min_range), 2)

    def __score_punctuation(self, punctuation_chars, word_chars):

        if word_chars == 0:
            return 0
        ratio = round((punctuation_chars/word_chars)*100, 1)
        
        if ratio >= self.PUNCTUATION_PERCENT_DESIRED_MIN and ratio <= self.PUNCTUATION_PERCENT_DESIRED_MAX:
            return 10.0
        elif ratio >= self.PUNCTUATION_PERCENT_BAD[0]:
            ratio = self.PUNCTUATION_PERCENT_MAX if ratio > self.PUNCTUATION_PERCENT_MAX else ratio
            min_value = self.PUNCTUATION_PERCENT_MAX
            max_value = self.PUNCTUATION_PERCENT_BAD[0]
            min_range = 0.0
            max_range = 5.0
        elif ratio >= self.PUNCTUATION_PERCENT_SEMIBAD[0]:
            min_value = self.PUNCTUATION_PERCENT_BAD[0]
            max_value = self.PUNCTUATION_PERCENT_SEMIBAD[0]
            min_range = 5.0
            max_range = 7.0
        elif ratio > self.PUNCTUATION_PERCENT_DESIRED_MAX:
            min_value = self.PUNCTUATION_PERCENT_SEMIBAD[0]
            max_value = self.PUNCTUATION_PERCENT_DESIRED_MAX
            min_range = 7.0
            max_range = 10.0
        elif ratio >= self.PUNCTUATION_PERCENT_SEMIBAD[1]:
            min_value = self.PUNCTUATION_PERCENT_SEMIBAD[1]
            max_value = self.PUNCTUATION_PERCENT_DESIRED_MIN
            min_range = 5.0
            max_range = 10.0
        else:
            min_value = 0.0
            max_value = self.PUNCTUATION_PERCENT_SEMIBAD[1]
            min_range = 0.0
            max_range = 5.0
            
        if min_value == max_value:
            return 0
        
        return round(((ratio - min_value) / (max_value - min_value) * (max_range - min_range) + min_range), 1)

    def __score_singular_chars(self, singular_chars, word_chars):

        if word_chars == 0:
            return 0
            
        ratio = round((singular_chars/word_chars)*100, 1)
        
        if ratio <= self.SINGULAR_CHARS_PERCENT_DESIRED:
            return 10.0
        elif ratio >= self.SINGULAR_CHARS_PERCENT_BAD:
            ratio = self.SINGULAR_CHARS_PERCENT_MAX if ratio > self.SINGULAR_CHARS_PERCENT_MAX else ratio
            min_value = self.SINGULAR_CHARS_PERCENT_MAX
            max_value = self.SINGULAR_CHARS_PERCENT_BAD
            min_range = 0.0
            max_range = 5.0
        elif ratio >= self.SINGULAR_CHARS_PERCENT_SEMIBAD:
            min_value = self.SINGULAR_CHARS_PERCENT_BAD
            max_value = self.SINGULAR_CHARS_PERCENT_SEMIBAD
            min_range = 5.0
            max_range = 7.0
        else:
            min_value = self.SINGULAR_CHARS_PERCENT_SEMIBAD
            max_value = self.SINGULAR_CHARS_PERCENT_DESIRED
            min_range = 7.0
            max_range = 10.0
        
        if min_value == max_value:
            return 0
        
        return round(((ratio - min_value) / (max_value - min_value) * (max_range - min_range) + min_range), 1)
        

    def __score_numbers(self, numbers, word_chars):
        
        if word_chars == 0:
            return 0
        numbers_ratio = round((numbers/word_chars)*100, 1)
        
        if numbers_ratio <= self.NUMBERS_PERCENT_DESIRED:
            return 10.0
        elif numbers_ratio >= self.NUMBERS_PERCENT_BAD:
            numbers_ratio = self.NUMBERS_PERCENT_MAX if numbers_ratio > self.NUMBERS_PERCENT_MAX else numbers_ratio
            min_value = self.NUMBERS_PERCENT_MAX
            max_value = self.NUMBERS_PERCENT_BAD
            min_range = 0.0
            max_range = 5.0
        elif numbers_ratio >= self.NUMBERS_PERCENT_SEMIBAD:
            min_value = self.NUMBERS_PERCENT_BAD
            max_value = self.NUMBERS_PERCENT_SEMIBAD
            min_range = 5.0
            max_range = 7.0
        else:
            min_value = self.NUMBERS_PERCENT_SEMIBAD
            max_value = self.NUMBERS_PERCENT_DESIRED
            min_range = 7.0
            max_range = 10.0
        
        if min_value == max_value:
            return 0
        
        return round(((numbers_ratio - min_value) / (max_value - min_value) * (max_range - min_range) + min_range), 1)

    def __score_repeated(self, document):
        repeated = [segment for segment in document.split("\n") if len(segment) >= self.MENUS_AVERAGE_LENGTH]
        if repeated:
            repeated = (len(repeated) - len(list(set(repeated))))/len(repeated)*10
            return round((repeated - 10) / - 10 * 10 , 1)
        else:
            return 10
            
    def __score_long_texts(self,  lang_segments, word_chars):
        if len(word_chars) != len(lang_segments):
            lang_segments = [self.ref_language]*len(word_chars) #dafuq?
            # return (-1000, -1000)
        
        long_segments = []
        for n in range(len(word_chars)):
            if lang_segments[n].split("_")[0] == self.ref_language and word_chars[n] >self.LONG_TEXT_MIN:
                useful_chars = self.LONG_TEXT_MAX if word_chars[n] > self.LONG_TEXT_MAX else word_chars[n]
                score = round((useful_chars - self.LONG_TEXT_MIN) / (self.LONG_TEXT_MAX - self.LONG_TEXT_MIN) * 10 , 1)
                long_segments.append(score)
                    
        n_segments = len(long_segments) if len(long_segments) <= 10 else 10
        highter_segments = [x for x in long_segments if x >  5]
        score_very_long_segments = 0.0
        if highter_segments:
            score_very_long_segments = (sum(highter_segments)+0.1*(len(highter_segments)))/len(highter_segments)
            
        score_n_segments = round(n_segments / self.DESIRED_LONG_TEXTS * 10, 2)
        return (score_n_segments if score_n_segments <= 10 else 10 , score_very_long_segments if score_very_long_segments <= 10 else 10)



## _____ MAIN SCORING FUNCTION _______________________________________________________________________________________________________________

    def score_text(self, lang_segments, scores_lang, document):

        condensed_data = [(len(re.findall(self.word_pattern, segment)), len(re.findall(self.punctuation_pattern, segment)), len(re.findall(self.singular_chars_pattern, segment)), len(re.findall(self.numbers_pattern, segment))) for segment in document.split("\n")]
    
        word_chars = [x[0] for x in condensed_data]
        punctuation_chars = [x[1] for x in condensed_data]
        singular_chars = [x[2] for x in condensed_data]
        numbers = [x[3] for x in condensed_data]
        
        language_score = self.__score_lang(lang_segments, scores_lang, word_chars)
        punctuation_score = self.__score_punctuation(sum(punctuation_chars), sum(word_chars))
        singular_chars_score = self.__score_singular_chars(sum(singular_chars), sum(word_chars))
        numbers_score = self.__score_numbers(sum(numbers), sum(word_chars))
        repeated_score = self.__score_repeated(document)
        url_score = self.__score_urls(document, word_chars)
        long_segments_scores = self.__score_long_texts(lang_segments, word_chars)
            
        
        score = (language_score*0.8 + long_segments_scores[0]/10 + long_segments_scores[1]/10) * custom_mean([url_score/10, punctuation_score/10, singular_chars_score/10, numbers_score/10, repeated_score/10])
        return [float(round(score, 1) if score <= 10 else 10), float(round(language_score, 1)), float(round(url_score, 1)), float(round(punctuation_score, 1)), float(round(singular_chars_score, 1)), float(round(numbers_score, 1)), float(round(repeated_score, 1)), float(round(long_segments_scores[0], 1)), float(round(long_segments_scores[1], 1))]#, document] #comment document if text is not wanted


    def score_document(self, raw_document, only_final_score=False):
        document = json.loads(raw_document)
        score = self.score_text(lang_segments=document["langs"], scores_lang=document["scores"], document=document["text"])
        if only_final_score:
            return score[0]
        else:
            return score
    
def score_directory(ref_lang, input_path, output_path, config):
    ds=DocumentScorer(ref_lang, config)
    for json_f in os.listdir(input_path):
        if json_f.endswith(".jsonl"):
            documents = os.path.join(input_path, json_f)
            file_name = os.path.splitext(os.path.basename(json_f))[0]
            writing_path = os.path.join(output_path, f"{file_name}.csv")
            df = pd.DataFrame(columns=["score"])
            
            i = 0
            logging.info(f"Processing: {file_name}")
            with open(documents, "r", encoding="utf-8") as file:
                n_lines = sum(1 for _ in file)
                logging.info(f"{file_name} - {n_lines} documents")
            with open(documents, "r", encoding="utf-8") as file:
                for document in file:
                    document_score = ds.score_document(document)
                    docid = json.loads(document)["id"]
                    df.loc[docid] = [document_score]
                    
                    i+=1
                    if i % 10000 == 0:
                        logging.info(f"{document['document_lang']} - {i}/{n_lines}")
                
            df["wds_score"] = df.score.apply(lambda x: x[0])
            df["language_score"] = df.score.apply(lambda x: x[1])
            df["url_score"] = df.score.apply(lambda x: x[2])
            df["punctuation_score"] = df.score.apply(lambda x: x[3])
            df["singular_chars_score"] = df.score.apply(lambda x: x[4])
            df["numbers_score"] = df.score.apply(lambda x: x[5])
            df["repeated_score"] = df.score.apply(lambda x: x[6])
            df["n_long_segments_score"] = df.score.apply(lambda x: x[7])
            df["great_segment_score"] = df.score.apply(lambda x: x[8])
            # df["text"] = df.score.apply(lambda x: x[9]) #comment if text is not wanted
            df.drop(columns=["score"], inplace=True)
            df.to_csv(writing_path)
            logging.info(f"Saved results in '{writing_path}'")


def main():
    #logging_setup()
    args = docopt.docopt(__doc__, version='printbook v 1.0')

    ref_lang = args["--lang"]
    if not ref_lang:
        logging.error("Missing 'lang' argument")
        sys.exit(-1)
        
    input_path=args['--input']
    if( not os.path.exists(input_path)):
        logging.error(f"File {input_path} not found")
        sys.exit(-1)

    output_path=args['--output']
    if not output_path:
        output_path = input_path+"/document_scores"
        if (not os.path.exists(output_path)):
            os.makedirs(output_path)
    if( not os.path.exists(output_path)):
        logging.error(f"Directory {output_path} not found")
        sys.exit(-1)

    config=args['--config']
    if not config:
        config=os.path.dirname(__file__)+"/language_adaption/medians_language.csv"
    if( not os.path.exists(config)):
        logging.error(f"File {config} not found")
        sys.exit(-1)
    

    logging.info("Executing main program...")
    
    score_directory(ref_lang, input_path, output_path, config)
    logging.info("Program finished")

if __name__ == '__main__':
    main()
