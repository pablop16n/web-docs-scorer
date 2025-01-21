"""
Usage:
  docscorer.py --input=<dir> [--output=<dir>] [--benchmark_config=<csv>] [--info_score_config=<dir>] [--lang_code_conversion=<json>] [--lang_families_config=<csv>] [--only_final_score=<y>] [--text_in_output=<y>]

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
try:
  from .modules.informativeness import Informativeness
except ImportError:
  from modules.informativeness import Informativeness

logging.basicConfig(
        level=logging.INFO,  
        format='%(asctime)s - %(levelname)s - %(message)s',
        stream=sys.stdout 
    )

args = docopt.docopt(__doc__, version='printbook v 1.0')

## _____ INPUT-OUTPUT _______________________________________________________________________________________________________________
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
    
## _____ CONFIGURATION FILES _______________________________________________________________________________________________________________
CONFIG = {
    #directories in CONFIG must be inicialized with a default value and other configuration values must be initially False
    "benchmark_config": os.path.dirname(__file__)+"/configurations/language_adaption/medians_language.csv", 
    "info_score_config": os.path.dirname(__file__)+"/configurations/interpolation_functions/",
    "lang_code_conversion": os.path.dirname(__file__)+"/configurations/language_adaption/lang_code_conversion.json",
    "lang_families_config": os.path.dirname(__file__)+"/configurations/language_adaption/lang_families_script.csv",
    "text_in_output": False,
    "only_final_score": False
}

for config_name, is_dir in CONFIG.items():
    selected_config = args[f"--{config_name}"]
    if CONFIG[config_name]:
        #Directories
        if selected_config:
            CONFIG[config_name] = selected_config #If not expressed, the default directory is used
        if( not os.path.exists(CONFIG[config_name])):
            logging.error(f"File {CONFIG[config_name]} for {config_name} not found")
            sys.exit(-1)
    else:
        #Config values
        if selected_config:
            CONFIG[config_name] = True

## _____ Class with all data and functions to be reused _______________________________________________________________________________________________________________
class DocumentScorer:
    def __init__(self):
        benchmark_config= CONFIG["benchmark_config"] if CONFIG else os.path.dirname(__file__)+"/configurations/language_adaption/medians_language.csv"
        info_score_config= CONFIG["info_score_config"] if CONFIG else os.path.dirname(__file__)+"/configurations/interpolation_functions"
        lang_code_conversion= CONFIG["lang_code_conversion"] if CONFIG else os.path.dirname(__file__)+"/configurations/language_adaption/lang_code_conversion.json"
        lang_families_config= CONFIG["lang_families_config"] if CONFIG else os.path.dirname(__file__)+"/configurations/language_adaption/lang_families_script.csv"

        ## _____ LANGUAGE CODE ADAPTION ________________________________________________________________________________________________
        with open(lang_code_conversion, "r", encoding="utf-8") as file:
            self.CODE_2_to_3_CONVERSION = json.load(file)


        ## _____ LANGUAGE ADAPTATION DATA ________________________________________________________________________________________________
        df_lang_adaption = pd.read_csv(benchmark_config)
        LANGUAGES = df_lang_adaption.language_3_chars.to_list()
        
        MODELED_LANGS_NUMBERS = {f"{line.language_3_chars}_{line.script}" : round(line.numbers_score, 1) for _, line in df_lang_adaption.iterrows()}
        MODELED_LANGS_PUNCTUATION = {f"{line.language_3_chars}_{line.script}" : round(line.punctuation_score, 1) for _, line in df_lang_adaption.iterrows()}
        MODELED_LANGS_SINGULAR_CHARS = {f"{line.language_3_chars}_{line.script}" : round(line.singular_chars_score, 1) for _, line in df_lang_adaption.iterrows()}
        
        ## _____ LANGUAGES_SCRIPTS ________________________________________________________________________________________________
        df_families = pd.read_csv(lang_families_config)
        df_lang_no_data = df_families[~df_families.language_3_chars.isin(LANGUAGES)]
        df_lang_data = df_families[df_families.language_3_chars.isin(LANGUAGES)]
        df_lang_adaption = pd.merge(df_lang_data, df_lang_adaption, on=['language_3_chars', 'script'], how='inner') #language families + medians in the same df

        for _, line in df_lang_no_data.iterrows():
            familiars = df_lang_adaption[(df_lang_adaption.genus == line.genus)&(df_lang_adaption.script == line.script)]
            if familiars.empty:
                familiars = df_lang_adaption[(df_lang_adaption.family == line.family)&(df_lang_adaption.script == line.script)]
            if not familiars.empty:
                MODELED_LANGS_NUMBERS[f"{line.language_3_chars}_{line.script}"] = round(average(familiars.numbers_score.to_list()), 2)
                MODELED_LANGS_PUNCTUATION[f"{line.language_3_chars}_{line.script}"] = round(average(familiars.punctuation_score.to_list()), 2)
                MODELED_LANGS_SINGULAR_CHARS[f"{line.language_3_chars}_{line.script}"] = round(average(familiars.singular_chars_score.to_list()), 2)
        
        del df_lang_adaption
        del df_families

        #equivalent script systems

        self.EQUIVALENT_SCRIPTS = {"hant": "hans"}

        ## _____ REFERENCE RATIO VALUES FOR SPANISH ________________________________________________________________________________________________
        #Current values in the provided csv    
        ref_punctuation = MODELED_LANGS_PUNCTUATION["spa_Latn"]
        ref_numbers = MODELED_LANGS_NUMBERS["spa_Latn"]
        ref_singular_chars = MODELED_LANGS_SINGULAR_CHARS["spa_Latn"]
        
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

        ## _____ MENUS ADAPTATION _______________________________________________________________________________________________________________
        self.MENUS_AVERAGE_LENGTH = {lang: round(ref_punctuation * menu_length / val) for lang, val in MODELED_LANGS_PUNCTUATION.items()}
        self.MENUS_AVERAGE_LENGTH["standard"] = average(self.MENUS_AVERAGE_LENGTH.values())
        
        ## _____ PUNCTUATION SCORING _______________________________________________________________________________________________________________
        self.PUNCTUATION_PERCENT_MAX = {lang: round(val * punct_max / ref_punctuation,1) if val * punct_max / ref_punctuation < 100 else 100.0 for lang, val in MODELED_LANGS_PUNCTUATION.items()}
        self.PUNCTUATION_PERCENT_MAX["standard"] = average(self.PUNCTUATION_PERCENT_MAX.values())
        
        self.PUNCTUATION_PERCENT_BAD = {lang: (round(val * punct_bad[0] / ref_punctuation,1), round(val * punct_bad[1] / ref_punctuation, 1)) for lang, val in MODELED_LANGS_PUNCTUATION.items()}
        self.PUNCTUATION_PERCENT_BAD["standard"] = (average([x[0] for x in self.PUNCTUATION_PERCENT_BAD.values()]), average([x[1] for x in self.PUNCTUATION_PERCENT_BAD.values()]))

        self.PUNCTUATION_PERCENT_SEMIBAD = {lang: (round(val * punct_semibad[0] / ref_punctuation,1), round(val * punct_semibad[1] / ref_punctuation, 1)) for lang, val in MODELED_LANGS_PUNCTUATION.items()}
        self.PUNCTUATION_PERCENT_SEMIBAD["standard"] = (average([x[0] for x in self.PUNCTUATION_PERCENT_SEMIBAD.values()]), average([x[1] for x in self.PUNCTUATION_PERCENT_SEMIBAD.values()]))

        self.PUNCTUATION_PERCENT_DESIRED_MAX = {lang: round(val * punct_desired_max / ref_punctuation,1) for lang, val in MODELED_LANGS_PUNCTUATION.items()}
        self.PUNCTUATION_PERCENT_DESIRED_MAX["standard"] = average(self.PUNCTUATION_PERCENT_DESIRED_MAX.values())

        self.PUNCTUATION_PERCENT_DESIRED_MIN  = {lang: round(val * punct_desired_min / ref_punctuation,1) for lang, val in MODELED_LANGS_PUNCTUATION.items()}
        self.PUNCTUATION_PERCENT_DESIRED_MIN["standard"] = average(self.PUNCTUATION_PERCENT_DESIRED_MIN.values())

        ## _____ SINGULAR CHARS SCORING _______________________________________________________________________________________________________________
        self.SINGULAR_CHARS_PERCENT_MAX = {lang: round(val * singular_chars_max / ref_singular_chars,1) if val * singular_chars_max / ref_singular_chars < 100 else 100.0 for lang, val in MODELED_LANGS_SINGULAR_CHARS.items()}
        self.SINGULAR_CHARS_PERCENT_MAX["standard"] = average(self.SINGULAR_CHARS_PERCENT_MAX.values())

        self.SINGULAR_CHARS_PERCENT_BAD = {lang: round(val * singular_chars_bad / ref_singular_chars,1) for lang, val in MODELED_LANGS_SINGULAR_CHARS.items()}
        self.SINGULAR_CHARS_PERCENT_BAD["standard"] = average(self.SINGULAR_CHARS_PERCENT_BAD.values())

        self.SINGULAR_CHARS_PERCENT_SEMIBAD = {lang: round(val * singular_chars_semibad / ref_singular_chars,1) for lang, val in MODELED_LANGS_SINGULAR_CHARS.items()}
        self.SINGULAR_CHARS_PERCENT_SEMIBAD["standard"] = average(self.SINGULAR_CHARS_PERCENT_SEMIBAD.values())

        self.SINGULAR_CHARS_PERCENT_DESIRED  = {lang: round(val * singular_chars_desired / ref_singular_chars,1) for lang, val in MODELED_LANGS_SINGULAR_CHARS.items()}
        self.SINGULAR_CHARS_PERCENT_DESIRED["standard"] = average(self.SINGULAR_CHARS_PERCENT_DESIRED.values())

        ## _____ NUMBERS SCORING _______________________________________________________________________________________________________________
        self.NUMBERS_PERCENT_MAX = {lang: round(val * numbers_max / ref_numbers,1) if val * numbers_max / ref_numbers < 100 else 100.0 for lang, val in MODELED_LANGS_NUMBERS.items()}
        self.NUMBERS_PERCENT_MAX["standard"] = average(self.NUMBERS_PERCENT_MAX.values())

        self.NUMBERS_PERCENT_BAD = {lang: round(val * numbers_bad / ref_numbers,1) if val * numbers_max / ref_numbers < 100 else 100.0 for lang, val in MODELED_LANGS_NUMBERS.items()}
        self.NUMBERS_PERCENT_BAD["standard"] = average(self.NUMBERS_PERCENT_BAD.values())

        self.NUMBERS_PERCENT_SEMIBAD = {lang: round(val * numbers_semibad / ref_numbers,1) for lang, val in MODELED_LANGS_NUMBERS.items()}
        self.NUMBERS_PERCENT_SEMIBAD["standard"] = average(self.NUMBERS_PERCENT_SEMIBAD.values())

        self.NUMBERS_PERCENT_DESIRED  = {lang: round(val * numbers_desired / ref_numbers,1) for lang, val in MODELED_LANGS_NUMBERS.items()}
        self.NUMBERS_PERCENT_DESIRED["standard"] = average(self.NUMBERS_PERCENT_DESIRED.values())

        ## _____ LONG SEGMENTS SCORING _______________________________________________________________________________________________________________
        self.LONG_TEXT_MAX = {lang: round(ref_punctuation * long_text_max / val) for lang, val in MODELED_LANGS_PUNCTUATION.items()}
        self.LONG_TEXT_MAX["standard"] = average(self.LONG_TEXT_MAX.values())

        self.LONG_TEXT_MIN = {lang: round(ref_punctuation * long_text_min / val) for lang, val in MODELED_LANGS_PUNCTUATION.items()}
        self.LONG_TEXT_MIN["standard"] = average(self.LONG_TEXT_MIN.values())

        # Number of long texts that means a 10 score
        self.DESIRED_LONG_TEXTS = 10
        
        ## _____ CHARS DETECTION _______________________________________________________________________________________________________________
        # Regex unicode codes for char-type count
        SINGULAR_CHARS = ["0023-0026", "002A-002B", "002F-002F", "003C-003E", "0040-0040", "005C-005C", "007C-007C", "007E-007E", "00A2-00B3", "00B8-00BE", "00D7-00D7", "00F7-00F7", "02B0-0385", "0483-0489", "0559-055F", "2010-2D00", "2DE0-2E52", "10000-1FFFF", "A670-A67F", "3200-33FF"]
        PUNCTUATION_CHARS = ["0021-0022", "0027-0029", "002C-002E", "003A-003B", "003F-003F", "005B-005B", "005D-005D", "0060-0060", "00A1-00A1", "00B4-00B5", "00B7-00B7", "00BF-00BF","0589-05C7", "0600-061F", "066A-066D", "06D4-06ED", "0700-070F", "1360-1368", "1800-180A", "1AB0-1AFF", "1C78-1C7F", "1CC0-1CC7", "1FBD-1FC1", "1FCD-1FCF", "1FDD-1FDF", "1FED-1FEF", "1FFD-2027", "3000-303F", "4DC0-4DFF", "A6F0-A6F7", "FE10-FE6F"]
        NUMBERS = ["0030-0039", "0660-0669", "06F0-06F9", "0964-096F", "09F2-09F9", "0B66-0B77", "0BE6-0BFA", "0C66-0C6F", "0C78-0C7E", "0CE6-0CEF", "0D66-0D79", "0DE6-0DEF", "0E50-0E5B", "0EC0-0ED9", "1040-1049", "1090-1099", "1369-137C", "17E0-17E9", "1810-1819", "19D0-19DA", "1A80-1A99", "1B50-1B59", "1C40-1C49", "1C50-1C59", "A830-A839", "A8D0-A8D9", "AA50-AA59"]
        SPACES = ["0000-0020", "007F-00A0", "2B7E-2B7E", "008A-008A", "0088-0088"]

        self.numbers_pattern = join_utf_blocks(NUMBERS)
        self.singular_chars_pattern = join_utf_blocks(SINGULAR_CHARS)
        self.punctuation_pattern = join_utf_blocks(PUNCTUATION_CHARS)
        self.word_pattern = join_utf_blocks(SINGULAR_CHARS + PUNCTUATION_CHARS + NUMBERS + SPACES, inverse=True) #alphabetic chars are considered by default
        # self.spaces_pattern = join_utf_blocks(SPACES)

        ## _____ INFORMATIVENESS SCORE _______________________________________________________________________________________________________________
        self.info = Informativeness(info_score_config)


    ## _____SCORING FUNCTIONS _______________________________________________________________________________________________________________
    def __score_lang(self, ref_language, lang_segments, scores_lang, word_chars, id):
        
        if scores_lang and (len(lang_segments) != len(scores_lang) or len(scores_lang) != len(word_chars)):
            return 10 #Errors from unmatched scores

        menu_length = self.MENUS_AVERAGE_LENGTH[ref_language] if ref_language in self.MENUS_AVERAGE_LENGTH else self.MENUS_AVERAGE_LENGTH["standard"]
        correct_lang_chars = 0
        wrong_lang_chars = 0
        available_chars = False
        for n in range(len(lang_segments)):
            if word_chars[n] <= menu_length:
                if lang_segments[n] == ref_language:
                    available_chars = True
                continue
            elif lang_segments[n] == ref_language:
                correct_lang_chars += word_chars[n]
            elif not scores_lang or scores_lang[n] > 0.2:
                wrong_lang_chars += word_chars[n]
        if correct_lang_chars == 0:
            if not available_chars:
                print(f"Doc_name: '{id}' -No available segments have been found on the target language -Language: '{ref_language}' -Segment_languages: {set(lang_segments)}")
            else:
                print(f"Doc_name: '{id}' -Only too short segments have been found on the target language")
            return 0
        results = (correct_lang_chars / (correct_lang_chars + wrong_lang_chars)*10)
        return round(results, 1) if results <= 10 else 10


    def __score_urls(self, ref_language, document, word_chars):
        menu_length = self.MENUS_AVERAGE_LENGTH[ref_language] if ref_language in self.MENUS_AVERAGE_LENGTH else self.MENUS_AVERAGE_LENGTH["standard"]
        n_segments = len([x for x in word_chars if x > menu_length])
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

    def __score_punctuation(self, ref_language, punctuation_chars, word_chars):
    
        percent_max = self.PUNCTUATION_PERCENT_MAX[ref_language] if ref_language in self.PUNCTUATION_PERCENT_MAX else self.PUNCTUATION_PERCENT_MAX["standard"]
        percent_bad = self.PUNCTUATION_PERCENT_BAD[ref_language] if ref_language in self.PUNCTUATION_PERCENT_BAD else self.PUNCTUATION_PERCENT_BAD["standard"]
        percent_semibad = self.PUNCTUATION_PERCENT_SEMIBAD[ref_language] if ref_language in self.PUNCTUATION_PERCENT_SEMIBAD else self.PUNCTUATION_PERCENT_SEMIBAD["standard"]
        percent_desired_max = self.PUNCTUATION_PERCENT_DESIRED_MAX[ref_language] if ref_language in self.PUNCTUATION_PERCENT_DESIRED_MAX else self.PUNCTUATION_PERCENT_DESIRED_MAX["standard"]
        percent_desired_min = self.PUNCTUATION_PERCENT_DESIRED_MIN[ref_language] if ref_language in self.PUNCTUATION_PERCENT_DESIRED_MIN else self.PUNCTUATION_PERCENT_DESIRED_MIN["standard"]
        
        if word_chars == 0:
            return 0
        ratio = round((punctuation_chars/word_chars)*100, 1)
        
        if ratio >= percent_desired_min and ratio <= percent_desired_max:
            return 10.0
        elif ratio >= percent_bad[0]:
            ratio = percent_max if ratio > percent_max else ratio
            min_value = percent_max
            max_value = percent_bad[0]
            min_range = 0.0
            max_range = 5.0
        elif ratio >= percent_semibad[0]:
            min_value = percent_bad[0]
            max_value = percent_semibad[0]
            min_range = 5.0
            max_range = 7.0
        elif ratio > percent_desired_max:
            min_value = percent_semibad[0]
            max_value = percent_desired_max
            min_range = 7.0
            max_range = 10.0
        elif ratio >= percent_semibad[1]:
            min_value = percent_semibad[1]
            max_value = percent_desired_min
            min_range = 5.0
            max_range = 10.0
        else:
            min_value = 0.0
            max_value = percent_semibad[1]
            min_range = 0.0
            max_range = 5.0
            
        if min_value == max_value:
            return 0
        
        return round(((ratio - min_value) / (max_value - min_value) * (max_range - min_range) + min_range), 1)

    def __score_singular_chars(self, ref_language, singular_chars, word_chars):
        percent_max = self.SINGULAR_CHARS_PERCENT_MAX[ref_language] if ref_language in self.SINGULAR_CHARS_PERCENT_MAX else self.SINGULAR_CHARS_PERCENT_MAX["standard"]
        percent_bad = self.SINGULAR_CHARS_PERCENT_BAD[ref_language] if ref_language in self.SINGULAR_CHARS_PERCENT_BAD else self.SINGULAR_CHARS_PERCENT_BAD["standard"]
        percent_semibad = self.SINGULAR_CHARS_PERCENT_SEMIBAD[ref_language] if ref_language in self.SINGULAR_CHARS_PERCENT_SEMIBAD else self.SINGULAR_CHARS_PERCENT_SEMIBAD["standard"]
        percent_desired = self.SINGULAR_CHARS_PERCENT_DESIRED[ref_language] if ref_language in self.SINGULAR_CHARS_PERCENT_DESIRED else self.SINGULAR_CHARS_PERCENT_DESIRED["standard"]
        if word_chars == 0:
            return 0
            
        ratio = round((singular_chars/word_chars)*100, 1)
        
        if ratio <= percent_desired:
            return 10.0
        elif ratio >= percent_bad:
            ratio = percent_max if ratio > percent_max else ratio
            min_value = percent_max
            max_value = percent_bad
            min_range = 0.0
            max_range = 5.0
        elif ratio >= percent_semibad:
            min_value = percent_bad
            max_value = percent_semibad
            min_range = 5.0
            max_range = 7.0
        else:
            min_value = percent_semibad
            max_value = percent_desired
            min_range = 7.0
            max_range = 10.0
        
        if min_value == max_value:
            return 0
        
        return round(((ratio - min_value) / (max_value - min_value) * (max_range - min_range) + min_range), 1)
        

    def __score_numbers(self, ref_language, numbers, word_chars):
        percent_max = self.NUMBERS_PERCENT_MAX[ref_language] if ref_language in self.NUMBERS_PERCENT_MAX else self.NUMBERS_PERCENT_MAX["standard"]
        percent_bad = self.NUMBERS_PERCENT_BAD[ref_language] if ref_language in self.NUMBERS_PERCENT_BAD else self.NUMBERS_PERCENT_BAD["standard"]
        percent_semibad = self.NUMBERS_PERCENT_SEMIBAD[ref_language] if ref_language in self.NUMBERS_PERCENT_SEMIBAD else self.NUMBERS_PERCENT_SEMIBAD["standard"]
        percent_desired = self.NUMBERS_PERCENT_DESIRED[ref_language] if ref_language in self.NUMBERS_PERCENT_DESIRED else self.NUMBERS_PERCENT_DESIRED["standard"]
        
        if word_chars == 0:
            return 0
        numbers_ratio = round((numbers/word_chars)*100, 1)
        
        if numbers_ratio <= percent_desired:
            return 10.0
        elif numbers_ratio >= percent_bad:
            numbers_ratio = percent_max if numbers_ratio > percent_max else numbers_ratio
            min_value = percent_max
            max_value = percent_bad
            min_range = 0.0
            max_range = 5.0
        elif numbers_ratio >= percent_semibad:
            min_value = percent_bad
            max_value = percent_semibad
            min_range = 5.0
            max_range = 7.0
        else:
            min_value = percent_semibad
            max_value = percent_desired
            min_range = 7.0
            max_range = 10.0
        
        if min_value == max_value:
            return 0
        
        return round(((numbers_ratio - min_value) / (max_value - min_value) * (max_range - min_range) + min_range), 1)

    def __score_repeated(self, ref_language, document):
        menu_length = self.MENUS_AVERAGE_LENGTH[ref_language] if ref_language in self.MENUS_AVERAGE_LENGTH else self.MENUS_AVERAGE_LENGTH["standard"]
        repeated = [segment for segment in document.split("\n") if len(segment) >= menu_length]
        if repeated:
            repeated = (len(repeated) - len(list(set(repeated))))/len(repeated)*10
            return round((repeated - 10) / - 10 * 10 , 1)
        else:
            return 10
            
    def __score_long_texts(self, ref_language, lang_segments, word_chars):
        if len(word_chars) != len(lang_segments):
            lang_segments = [ref_language]*len(word_chars)
            # return (-1000, -1000)
        
        long_text_min = self.LONG_TEXT_MIN[ref_language] if ref_language in self.LONG_TEXT_MIN else self.LONG_TEXT_MIN["standard"]
        long_text_max = self.LONG_TEXT_MAX[ref_language] if ref_language in self.LONG_TEXT_MAX else self.LONG_TEXT_MAX["standard"]

        long_segments = []
        for n in range(len(word_chars)):
            if lang_segments[n] == ref_language and word_chars[n] > long_text_min:
                useful_chars = long_text_max if word_chars[n] > long_text_max else word_chars[n]
                score = round((useful_chars - long_text_min) / (long_text_max - long_text_min) * 10 , 1)
                long_segments.append(score)
                    
        n_segments = len(long_segments) if len(long_segments) <= 10 else 10
        highter_segments = [x for x in long_segments if x >  5]
        score_very_long_segments = 0.0
        if highter_segments:
            score_very_long_segments = (sum(highter_segments)+0.1*(len(highter_segments)))/len(highter_segments)
            
        score_n_segments = round(n_segments / self.DESIRED_LONG_TEXTS * 10, 2)
        return (score_n_segments if score_n_segments <= 10 else 10 , score_very_long_segments if score_very_long_segments <= 10 else 10)



## _____ MAIN SCORING FUNCTION _______________________________________________________________________________________________________________

    def score_text(self, ref_lang, lang_segments, scores_lang, document_text, script_sys, id, raw_score):

        condensed_data = [(len(re.findall(self.word_pattern, segment)), len(re.findall(self.punctuation_pattern, segment)), len(re.findall(self.singular_chars_pattern, segment)), len(re.findall(self.numbers_pattern, segment))) for segment in document_text.split("\n")]
    
        word_chars = [x[0] for x in condensed_data]
        punctuation_chars = [x[1] for x in condensed_data]
        singular_chars = [x[2] for x in condensed_data]
        numbers = [x[3] for x in condensed_data]
        ref_lang = ref_lang[0] if type(ref_lang) == list else ref_lang
        language_score = self.__score_lang(ref_lang, lang_segments, scores_lang, word_chars, id)
        punctuation_score = self.__score_punctuation(ref_lang, sum(punctuation_chars), sum(word_chars))
        singular_chars_score = self.__score_singular_chars(ref_lang, sum(singular_chars), sum(word_chars))
        numbers_score = self.__score_numbers(ref_lang, sum(numbers), sum(word_chars))
        repeated_score = self.__score_repeated(ref_lang, document_text)
        url_score = self.__score_urls(ref_lang, document_text, word_chars)
        long_segments_scores = self.__score_long_texts(ref_lang, lang_segments, word_chars)
        informativeness_score = self.info.rate_information(document_text, script_sys)
        
        score = (language_score*0.8 + long_segments_scores[0]/10 + long_segments_scores[1]/10) * custom_mean([url_score/10, punctuation_score/10, singular_chars_score/10, numbers_score/10, repeated_score/10, informativeness_score/10])

        if raw_score:
            return round(score, 1) if score <= 10 else 10
        
        final_score = [round(score, 1) if score <= 10 else 10, round(language_score, 1), round(url_score, 1), round(punctuation_score, 1), round(singular_chars_score, 1), round(numbers_score, 1), round(repeated_score, 1), round(long_segments_scores[0], 1), round(long_segments_scores[1], 1), round(informativeness_score, 1)] 
        
        if CONFIG and CONFIG["text_in_output"]:
            final_score.append(document_text.replace("\n", "\\n")) 
        return final_score

    def score_document(self, document, raw_score=False):
        return self.score_text(ref_lang=f"{document['document_lang']}_{document['script']}", lang_segments=document["langs"], scores_lang=document["scores"] if "scores" in document else False, document_text=document["text"], script_sys=document["script"], id=document["id"], raw_score=raw_score)
        
    
def score_directory(input_path, output_path):
    ds=DocumentScorer()
    for json_f in os.listdir(input_path):
        if json_f.endswith(".jsonl"):
            if not re.match("[a-z]{3}_[A-Z][a-z]{3}$", json_f.split(".")[0]):
                logging.error(f"{json_f} is not a well formed named → eng_Latn.jsonl")
                continue
            documents = os.path.join(input_path, json_f)
            file_name = os.path.splitext(os.path.basename(json_f))[0]
            writing_path = os.path.join(output_path, f"{file_name}.csv")
            df = pd.DataFrame(columns=["score"])

            lang_script = json_f.split(".")[0].split("_")
            language = lang_script[0].lower()
            script = lang_script[1].lower()
            script = ds.EQUIVALENT_SCRIPTS[script] if script in ds.EQUIVALENT_SCRIPTS else script
            
            i = 0
            logging.info(f"Processing: {file_name}")
            with open(documents, "r", encoding="utf-8") as file:
                n_lines = sum(1 for _ in file)
                logging.info(f"{file_name} - {n_lines} documents")
            with open(documents, "r", encoding="utf-8") as file:
                for document in file:
                    document = json.loads(document)
                    document["document_lang"] = language
                    document["script"] = script
                    langs_fixed = []
                    for x in document["langs"]:
                        x=x.lower()
                        #Script is added if "langs" includes language codes without script code
                        if re.match("[a-z]{3}$", x):
                            langs_fixed.append(f"{x}_{script}")
                        elif re.match("[a-z]{3}_[a-z]{4}$", x):
                            #Fix for very similar scripts or scripts that we want to be intended as the same, like Hans - Hant
                            segm_lang_script = x.split("_")
                            segm_script = ds.EQUIVALENT_SCRIPTS[segm_lang_script[1]] if segm_lang_script[1] in ds.EQUIVALENT_SCRIPTS else segm_lang_script[1]
                            langs_fixed.append(f"{segm_lang_script[0]}_{segm_script}")
                        else:
                            langs_fixed.append(x)
                    
                    document["langs"] = langs_fixed
                    document_score = ds.score_document(document=document)
                    docid = document["id"]
                    df.loc[docid] = [document_score]
                    
                    i+=1
                    if i % 10000 == 0:
                        logging.info(f"{document['document_lang']} - {i}/{n_lines}")

            df["wds_score"] = df.score.apply(lambda x: x[0])
            if not CONFIG["only_final_score"]:
                df["language_score"] = df.score.apply(lambda x: x[1])
                df["url_score"] = df.score.apply(lambda x: x[2])
                df["punctuation_score"] = df.score.apply(lambda x: x[3])
                df["singular_chars_score"] = df.score.apply(lambda x: x[4])
                df["numbers_score"] = df.score.apply(lambda x: x[5])
                df["repeated_score"] = df.score.apply(lambda x: x[6])
                df["n_long_segments_score"] = df.score.apply(lambda x: x[7])
                df["great_segment_score"] = df.score.apply(lambda x: x[8])
                df["informativeness_score"] = df.score.apply(lambda x: x[9])
            if CONFIG["text_in_output"]:
                df["text"] = df.score.apply(lambda x: x[10])
            df.drop(columns=["score"], inplace=True)
            df.to_csv(writing_path)
            logging.info(f"Saved results in '{writing_path}'")


def main():
    logging.info("Executing main program...")
    
    score_directory(input_path, output_path)
    logging.info("Program finished")

if __name__ == '__main__':
    main()
