"""
Usage:
  crawled_text_qualifier.py --input=<dir> --output=<dir>

"""


import docopt
import os
import pandas as pd
import re
import json
import sys


args = docopt.docopt(__doc__, version='printbook v 1.0')


## _____ LANGUAGE SCORING _______________________________________________________________________________________________________________
MENUS_AVERAGE_LENGTH = {"standard": 25, 'en': 24, 'ru': 22, 'vi': 23, 'ja': 12, 'zh': 6, 'mr': 25, 'fi': 24, 'nb': 24, 'sq': 24, 'fa': 24, 'lt': 23, 'et': 24, 'eo': 21, 'de': 24, 'lv': 23, 'so': 25, 'hi': 26, 'ca': 22, 'el': 24, 'be': 22, 'ga': 25, 'tl': 23, 'he': 21, 'sl': 23, 'ko': 10, 'ka': 23, 'la': 23, 'tr': 25, 'th': 29, 'hbs': 22, 'ar': 25, 'cs': 23, 'bn': 27, 'id': 25, 'te': 21, 'hu': 23, 'da': 24, 'mn': 23, 'mt': 13, 'es': 25, 'sk': 24, 'pl': 24, 'az': 24, 'af': 21, 'fr': 22, 'kk': 23, 'kn': 24, 'ne': 28, 'tt': 20, 'sv': 26, 'is': 26, 'pt': 23, 'it': 24, 'hy': 22, 'uk': 22, 'ms': 20, 'pa': 26, 'cy': 23, 'my': 31, 'ta': 24, 'bg': 23, 'ky': 23, 'nn': 24, 'ur': 26, 'eu': 24, 'si': 22, 'gu': 25, 'nl': 25, 'ps': 27, 'uz': 18, 'ro': 23, 'ml': 22, 'gl': 25, 'sw': 24, 'mk': 25}
# 2.6 bad_chars median of Spanish == 25, 7.2 bad_chars median of Korean == 10 (Median of bad chars of the best 20% of language evaluation in a +10k sample)

LANG_DET_FIX = {'standard': 6.5, 'af': 6.0, 'ar': 8.1, 'az': 7.1, 'be': 8.8, 'bg': 8.4, 'bn': 8.4, 'ca': 8.5, 'cs': 8.2, 'cy': 8.8, 'da': 8.2, 'de': 8.4, 'el': 8.6, 'en': 8.3, 'eo': 8.0, 'es': 8.5, 'et': 8.1, 'eu': 8.8, 'fa': 8.2, 'fi': 8.1, 'fr': 8.5, 'ga': 7.2, 'gl': 8.1, 'gu': 8.0, 'hbs': 0.0, 'he': 8.0, 'hi': 7.7, 'hu': 8.4, 'hy': 9.1, 'id': 7.9, 'is': 7.6, 'it': 8.4, 'ja': 5.4, 'ka': 8.8, 'kk': 9.0, 'kn': 8.2, 'ko': 5.9, 'ky': 8.7, 'la': 7.3, 'lt': 8.5, 'lv': 8.2, 'mk': 9.0, 'ml': 8.0, 'mn': 8.6, 'mr': 8.3, 'ms': 3.2, 'mt': 6.7, 'my': 8.0, 'nb': 7.8, 'ne': 8.5, 'nl': 8.3, 'nn': 7.3, 'pa': 8.2, 'pl': 8.2, 'ps': 8.4, 'pt': 8.4, 'ro': 7.9, 'ru': 8.4, 'si': 8.0, 'sk': 8.2, 'sl': 8.2, 'so': 4.6, 'sq': 8.8, 'sv': 8.3, 'sw': 7.3, 'ta': 8.4, 'te': 7.1, 'th': 6.7, 'tl': 7.5, 'tr': 8.7, 'tt': 6.6, 'uk': 8.7, 'ur': 7.5, 'uz': 7.3, 'vi': 8.3, 'zh': 3.8}
#LANG_DET_FIX contains the median of best 20% of language score, extracted with a non fixed valorate_lang() function

LANG_FIX_MEANING = 8.3
# Score of Spanish is used to fix the imbalance between languages of the language detector



## _____ BAD CHARS SCORING _______________________________________________________________________________________________________________
PERCENT_BAD_CHARS_MAX = {"standard": 30.5, 'ru': 32.0 , 'en': 30.4 , 'vi': 31.3 , 'ja': 38.5 , 'zh': 44.6 , 'mr': 30.2, 'fi': 30.4, 'nb': 30.4, 'sq': 30.7, 'fa': 30.4, 'lt': 31.3, 'et': 30.7, 'eo': 32.4, 'de': 30.7, 'lv': 31.5, 'so': 30.0, 'hi': 29.1, 'ca': 32.0, 'el': 30.9, 'be': 32.2, 'ga': 30.0, 'tl': 31.3, 'he': 32.8, 'sl': 31.1, 'ko': 40, 'ka': 31.1, 'la': 31.3, 'tr': 30.0, 'th': 27.4, 'hbs': 32.2, 'ar': 30.0, 'cs': 31.3, 'bn': 28.5, 'id': 30.2, 'te': 32.4, 'hu': 31.3, 'da': 30.9, 'mn': 31.3, 'mt': 37.8, 'es': 30.0, 'sk': 30.9, 'pl': 30.7, 'az': 30.9, 'af': 32.4, 'fr': 32.2, 'kk': 31.1, 'kn': 30.7, 'ne': 27.8, 'tt': 33.5, 'sv': 29.6, 'is': 29.6, 'pt': 31.3, 'it': 30.9, 'hy': 31.7, 'uk': 31.7, 'ms': 33.3, 'pa': 29.6, 'cy': 31.3, 'my': 26.3, 'ta': 30.7, 'bg': 31.5, 'ky': 31.1, 'nn': 30.9, 'ur': 29.1, 'eu': 30.9, 'si': 32.2, 'gu': 30.0, 'nl': 29.8, 'ps': 28.9, 'uz': 34.8, 'ro': 31.3, 'ml': 31.7, 'gl': 29.8, 'sw': 30.7, 'mk': 30.0}
# bad chars ratio maximum - min 30 máx 40, reference min 2.6 (es) reference max 7.2 (ko) which is the ratio of bad chars median of the best 20% language score
PERCENT_BAD_CHARS_SEMIBAD = {"standard": (10.0, 0.8), 'en': (10.2 , 0.8), 'ru': (11.0 , 1), 'vi': (10.7 , 0.9), 'ja': (14.2 , 1.6), 'zh': (17.3 , 2.1), 'mr': (10.1, 0.8), 'fi': (10.2, 0.8), 'nb': (10.2, 0.8), 'sq': (10.3, 0.9), 'fa': (10.2, 0.8), 'lt': (10.7, 0.9), 'et': (10.3, 0.9), 'eo': (11.2, 1.0), 'de': (10.3, 0.9), 'lv': (10.8, 0.9), 'so': (10.0, 0.8), 'hi': (9.6, 0.7), 'ca': (11.0, 1.0), 'el': (10.4, 0.9), 'be': (11.1, 1.0), 'ga': (10.0, 0.8), 'tl': (10.7, 0.9), 'he': (11.4, 1.1), 'sl': (10.5, 0.9), 'ko': (15.0, 1.7), 'ka': (10.5, 0.9), 'la': (10.7, 0.9), 'tr': (10.0, 0.8), 'th': (8.7, 0.6), 'hbs': (11.1, 1.0), 'ar': (10.0, 0.8), 'cs': (10.7, 0.9), 'bn': (9.2, 0.7), 'id': (10.1, 0.8), 'te': (11.2, 1.0), 'hu': (10.7, 0.9), 'da': (10.4, 0.9), 'mn': (10.7, 0.9), 'mt': (13.9, 1.5), 'es': (10.0, 0.8), 'sk': (10.4, 0.9), 'pl': (10.3, 0.9), 'az': (10.4, 0.9), 'af': (11.2, 1.0), 'fr': (11.1, 1.0), 'kk': (10.5, 0.9), 'kn': (10.3, 0.9), 'ne': (8.9, 0.6), 'tt': (11.7, 1.1), 'sv': (9.8, 0.8), 'is': (9.8, 0.8), 'pt': (10.7, 0.9), 'it': (10.4, 0.9), 'hy': (10.9, 1.0), 'uk': (10.9, 1.0), 'ms': (11.6, 1.1), 'pa': (9.8, 0.8), 'cy': (10.7, 0.9), 'my': (8.2, 0.5), 'ta': (10.3, 0.9), 'bg': (10.8, 0.9), 'ky': (10.5, 0.9), 'nn': (10.4, 0.9), 'ur': (9.6, 0.7), 'eu': (10.4, 0.9), 'si': (11.1, 1.0), 'gu': (10.0, 0.8), 'nl': (9.9, 0.8), 'ps': (9.5, 0.7), 'uz': (12.4, 1.2), 'ro': (10.7, 0.9), 'ml': (10.9, 1.0), 'gl': (9.9, 0.8), 'sw': (10.3, 0.9), 'mk': (10.0, 0.8)} #too many, too few
#SEMIBAD 10 & 0.8 min and +15 & 1.7 máx, reference min 2.6 (es) reference max 7.2 (ko) which is the ratio of bad chars median of the best 20% language score
PERCENT_BAD_CHARS_BAD = {"standard": (15.0, 0.5), 'en': (15.2, 0.5), 'ru': (16.0 , 0.6), 'vi': (15.7 , 0.5), 'ja': (19.2 , 0.8), 'zh': (22.3 , 0.9), 'mr': (15.1, 0.5), 'fi': (15.2, 0.5), 'nb': (15.2, 0.5), 'sq': (15.3, 0.5), 'fa': (15.2, 0.5), 'lt': (15.7, 0.5), 'et': (15.3, 0.5), 'eo': (16.2, 0.6), 'de': (15.3, 0.5), 'lv': (15.8, 0.5), 'so': (15.0, 0.5), 'hi': (14.6, 0.5), 'ca': (16.0, 0.6), 'el': (15.4, 0.5), 'be': (16.1, 0.6), 'ga': (15.0, 0.5), 'tl': (15.7, 0.5), 'he': (16.4, 0.6), 'sl': (15.5, 0.5), 'ko': (20.0, 0.8), 'ka': (15.5, 0.5), 'la': (15.7, 0.5), 'tr': (15.0, 0.5), 'th': (13.7, 0.4), 'hbs': (16.1, 0.6), 'ar': (15.0, 0.5), 'cs': (15.7, 0.5), 'bn': (14.2, 0.5), 'id': (15.1, 0.5), 'te': (16.2, 0.6), 'hu': (15.7, 0.5), 'da': (15.4, 0.5), 'mn': (15.7, 0.5), 'mt': (18.9, 0.7), 'es': (15.0, 0.5), 'sk': (15.4, 0.5), 'pl': (15.3, 0.5), 'az': (15.4, 0.5), 'af': (16.2, 0.6), 'fr': (16.1, 0.6), 'kk': (15.5, 0.5), 'kn': (15.3, 0.5), 'ne': (13.9, 0.4), 'tt': (16.7, 0.6), 'sv': (14.8, 0.5), 'is': (14.8, 0.5), 'pt': (15.7, 0.5), 'it': (15.4, 0.5), 'hy': (15.9, 0.6), 'uk': (15.9, 0.6), 'ms': (16.6, 0.6), 'pa': (14.8, 0.5), 'cy': (15.7, 0.5), 'my': (13.2, 0.4), 'ta': (15.3, 0.5), 'bg': (15.8, 0.5), 'ky': (15.5, 0.5), 'nn': (15.4, 0.5), 'ur': (14.6, 0.5), 'eu': (15.4, 0.5), 'si': (16.1, 0.6), 'gu': (15.0, 0.5), 'nl': (14.9, 0.5), 'ps': (14.5, 0.5), 'uz': (17.4, 0.6), 'ro': (15.7, 0.5), 'ml': (15.9, 0.6), 'gl': (14.9, 0.5), 'sw': (15.3, 0.5), 'mk': (15.0, 0.5)}
#BAD 15-0.5 min 20-0.8 máx, reference min 2.6 (es) reference max 7.2 (ko) which is the ratio of bad chars median of the best 20% language score

PERCENT_BAD_CHARS_DESIRED_MIN = {"standard": 1.2, 'en': 1.1 , 'ru': 1.4 , 'vi': 1.3 , 'ja': 2.7 , 'zh': 3.9 , 'mr': 1.0, 'fi': 1.1, 'nb': 1.1, 'sq': 1.1, 'fa': 1.1, 'lt': 1.3, 'et': 1.1, 'eo': 1.5, 'de': 1.1, 'lv': 1.3, 'so': 1.0, 'hi': 0.8, 'ca': 1.4, 'el': 1.2, 'be': 1.4, 'ga': 1.0, 'tl': 1.3, 'he': 1.6, 'sl': 1.2, 'ko': 3, 'ka': 1.2, 'la': 1.3, 'tr': 1.0, 'th': 0.5, 'hbs': 1.4, 'ar': 1.0, 'cs': 1.3, 'bn': 0.7, 'id': 1.0, 'te': 1.5, 'hu': 1.3, 'da': 1.2, 'mn': 1.3, 'mt': 2.6, 'es': 1.0, 'sk': 1.2, 'pl': 1.1, 'az': 1.2, 'af': 1.5, 'fr': 1.4, 'kk': 1.2, 'kn': 1.1, 'ne': 0.6, 'tt': 1.7, 'sv': 0.9, 'is': 0.9, 'pt': 1.3, 'it': 1.2, 'hy': 1.3, 'uk': 1.3, 'ms': 1.7, 'pa': 0.9, 'cy': 1.3, 'my': 0.3, 'ta': 1.1, 'bg': 1.3, 'ky': 1.2, 'nn': 1.2, 'ur': 0.8, 'eu': 1.2, 'si': 1.4, 'gu': 1.0, 'nl': 1.0, 'ps': 0.8, 'uz': 2.0, 'ro': 1.3, 'ml': 1.3, 'gl': 1.0, 'sw': 1.1, 'mk': 1.0}
#DESIRED 1 min 3 máx, reference min 2.6 (es) reference max 7.2 (ko) which is the ratio of bad chars median of the best 20% language score
PERCENT_BAD_CHARS_DESIRED_MAX = {'standard': 3.2, 'en': 3.1, 'ru': 3.4, 'vi': 3.3, 'ja': 4.7, 'zh': 5.9, 'mr': 3.0, 'fi': 3.1, 'nb': 3.1, 'sq': 3.1, 'fa': 3.1, 'lt': 3.3, 'et': 3.1, 'eo': 3.5, 'de': 3.1, 'lv': 3.3, 'so': 3.0, 'hi': 2.8, 'ca': 3.4, 'el': 3.2, 'be': 3.4, 'ga': 3.0, 'tl': 3.3, 'he': 3.6, 'sl': 3.2, 'ko': 5, 'ka': 3.2, 'la': 3.3, 'tr': 3.0, 'th': 2.5, 'hbs': 3.4, 'ar': 3.0, 'cs': 3.3, 'bn': 2.7, 'id': 3.0, 'te': 3.5, 'hu': 3.3, 'da': 3.2, 'mn': 3.3, 'mt': 4.6, 'es': 3.0, 'sk': 3.2, 'pl': 3.1, 'az': 3.2, 'af': 3.5, 'fr': 3.4, 'kk': 3.2, 'kn': 3.1, 'ne': 2.6, 'tt': 3.7, 'sv': 2.9, 'is': 2.9, 'pt': 3.3, 'it': 3.2, 'hy': 3.3, 'uk': 3.3, 'ms': 3.7, 'pa': 2.9, 'cy': 3.3, 'my': 2.3, 'ta': 3.1, 'bg': 3.3, 'ky': 3.2, 'nn': 3.2, 'ur': 2.8, 'eu': 3.2, 'si': 3.4, 'gu': 3.0, 'nl': 3.0, 'ps': 2.8, 'uz': 4.0, 'ro': 3.3, 'ml': 3.3, 'gl': 3.0, 'sw': 3.1, 'mk': 3.0}
#PERCENT_BAD_CHARS_DESIRED_MIN + 2



## _____ URL SCORING _______________________________________________________________________________________________________________
URL_ADMISSIBLE= {"standard": 0.003, 'en': 0.003, 'ru': 0.0038, 'vi': 0.0034, 'ja': 0.007, 'zh': 0.01, 'mr': 0.0029, 'fi': 0.003, 'nb': 0.003, 'sq': 0.0031, 'fa': 0.003, 'lt': 0.0034, 'et': 0.0031, 'eo': 0.004, 'de': 0.0031, 'lv': 0.0036, 'so': 0.0028, 'hi': 0.0024, 'ca': 0.0038, 'el': 0.0032, 'be': 0.0039, 'ga': 0.0028, 'tl': 0.0034, 'he': 0.0042, 'sl': 0.0033, 'ko': 0.0078, 'ka': 0.0033, 'la': 0.0034, 'tr': 0.0028, 'th': 0.0015, 'hbs': 0.0039, 'ar': 0.0028, 'cs': 0.0034, 'bn': 0.002, 'id': 0.0029, 'te': 0.004, 'hu': 0.0034, 'da': 0.0032, 'mn': 0.0034, 'mt': 0.0067, 'es': 0.0028, 'sk': 0.0032, 'pl': 0.0031, 'az': 0.0032, 'af': 0.004, 'fr': 0.0039, 'kk': 0.0033, 'kn': 0.0031, 'ne': 0.0017, 'tt': 0.0045, 'sv': 0.0026, 'is': 0.0026, 'pt': 0.0034, 'it': 0.0032, 'hy': 0.0037, 'uk': 0.0037, 'ms': 0.0044, 'pa': 0.0026, 'cy': 0.0034, 'my': 0.001, 'ta': 0.0031, 'bg': 0.0036, 'ky': 0.0033, 'nn': 0.0032, 'ur': 0.0024, 'eu': 0.0032, 'si': 0.0039, 'gu': 0.0028, 'nl': 0.0027, 'ps': 0.0023, 'uz': 0.0052, 'ro': 0.0034, 'ml': 0.0037, 'gl': 0.0027, 'sw': 0.0031, 'mk': 0.0028}
# 0.0028 of Spanish is used for extract others, using the ratio of bad chars median of the best 20% language score
URL_MAX = {"standard": 0.02, 'en': 0.02, 'ru': 0.026, 'vi': 0.023, 'ja': 0.048, 'zh': 0.068, 'mr': 0.0197, 'fi': 0.0205, 'nb': 0.0205, 'sq': 0.0212, 'fa': 0.0205, 'lt': 0.0234, 'et': 0.0212, 'eo': 0.027, 'de': 0.0212, 'lv': 0.0241, 'so': 0.019, 'hi': 0.0161, 'ca': 0.0256, 'el': 0.0219, 'be': 0.0263, 'ga': 0.019, 'tl': 0.0234, 'he': 0.0285, 'sl': 0.0227, 'ko': 0.0526, 'ka': 0.0227, 'la': 0.0234, 'tr': 0.019, 'th': 0.0102, 'hbs': 0.0263, 'ar': 0.019, 'cs': 0.0234, 'bn': 0.0139, 'id': 0.0197, 'te': 0.027, 'hu': 0.0234, 'da': 0.0219, 'mn': 0.0234, 'mt': 0.0453, 'es': 0.019, 'sk': 0.0219, 'pl': 0.0212, 'az': 0.0219, 'af': 0.027, 'fr': 0.0263, 'kk': 0.0227, 'kn': 0.0212, 'ne': 0.0117, 'tt': 0.0307, 'sv': 0.0175, 'is': 0.0175, 'pt': 0.0234, 'it': 0.0219, 'hy': 0.0248, 'uk': 0.0248, 'ms': 0.03, 'pa': 0.0175, 'cy': 0.0234, 'my': 0.0066, 'ta': 0.0212, 'bg': 0.0241, 'ky': 0.0227, 'nn': 0.0219, 'ur': 0.0161, 'eu': 0.0219, 'si': 0.0263, 'gu': 0.019, 'nl': 0.0183, 'ps': 0.0153, 'uz': 0.0351, 'ro': 0.0234, 'ml': 0.0248, 'gl': 0.0183, 'sw': 0.0212, 'mk': 0.019}
# 0.019 of Spanish is used for extract others, using the ratio of bad chars median of the best 20% language score



## _____ NUMBER SCORING _______________________________________________________________________________________________________________
PERCENT_NUMBERS_MAX = {"standard": 30, 'en': 28.8, 'ru': 31.2, 'vi': 33.8, 'ja': 41.2, 'zh': 57.3, 'mr': 30.8, 'fi': 30.4, 'nb': 29.6, 'sq': 31.9, 'fa': 30.4, 'lt': 29.6, 'et': 30.0, 'eo': 29.6, 'de': 29.2, 'lv': 30.4, 'so': 30.4, 'hi': 35.0, 'ca': 30.8, 'el': 31.5, 'be': 31.5, 'ga': 29.2, 'tl': 30.4, 'he': 28.5, 'sl': 30.0, 'ko': 50.0, 'ka': 31.5, 'la': 27.3, 'tr': 30.4, 'th': 32.7, 'hbs': 36.2, 'ar': 31.9, 'cs': 30.8, 'bn': 29.2, 'id': 30.0, 'te': 29.6, 'hu': 29.2, 'da': 30.0, 'mn': 35.8, 'mt': 30.4, 'es': 30.0, 'sk': 30.4, 'pl': 30.4, 'az': 33.1, 'af': 31.5, 'fr': 30.0, 'kk': 33.1, 'kn': 30.4, 'ne': 34.6, 'tt': 34.6, 'sv': 29.6, 'is': 30.4, 'pt': 31.2, 'it': 30.8, 'hy': 35.4, 'uk': 30.4, 'ms': 37.3, 'pa': 32.7, 'cy': 28.8, 'my': 33.5, 'ta': 31.2, 'bg': 30.8, 'ky': 30.4, 'nn': 30.8, 'ur': 31.5, 'eu': 30.0, 'si': 31.2, 'gu': 30.8, 'nl': 29.2, 'ps': 30.8, 'uz': 31.9, 'ro': 31.5, 'ml': 28.5, 'gl': 31.5, 'sw': 33.1, 'mk': 30.8}
# MAX 30 min 50 max
PERCENT_NUMBERS_BAD = {"standard": 15, 'en': 13.6, 'ru': 16.4, 'vi': 19.8, 'ja': 28.9, 'zh': 49.1, 'mr': 16.0, 'fi': 15.5, 'nb': 14.5, 'sq': 17.4, 'fa': 15.5, 'lt': 14.5, 'et': 15.0, 'eo': 14.5, 'de': 14.0, 'lv': 15.5, 'so': 15.5, 'hi': 21.3, 'ca': 16.0, 'el': 16.9, 'be': 16.9, 'ga': 14.0, 'tl': 15.5, 'he': 13.1, 'sl': 15.0, 'ko': 40.0, 'ka': 16.9, 'la': 11.6, 'tr': 15.5, 'th': 18.4, 'hbs': 22.7, 'ar': 17.4, 'cs': 16.0, 'bn': 14.0, 'id': 15.0, 'te': 14.5, 'hu': 14.0, 'da': 15.0, 'mn': 22.2, 'mt': 15.5, 'es': 15.0, 'sk': 15.5, 'pl': 15.5, 'az': 18.8, 'af': 16.9, 'fr': 15.0, 'kk': 18.8, 'kn': 15.5, 'ne': 20.8, 'tt': 20.8, 'sv': 14.5, 'is': 15.5, 'pt': 16.4, 'it': 16.0, 'hy': 21.7, 'uk': 15.5, 'ms': 24.1, 'pa': 18.4, 'cy': 13.6, 'my': 19.3, 'ta': 16.4, 'bg': 16.0, 'ky': 15.5, 'nn': 16.0, 'ur': 16.9, 'eu': 15.0, 'si': 16.4, 'gu': 16.0, 'nl': 14.0, 'ps': 16.0, 'uz': 17.4, 'ro': 16.9, 'ml': 13.1, 'gl': 16.9, 'sw': 18.8, 'mk': 16.0}
# BAD 15 min 40 max
PERCENT_NUMBERS_SEMIBAD = {"standard": 10, 'en': 8.8, 'ru': 11.2, 'vi': 13.8, 'ja': 21.2, 'zh': 37.3, 'mr': 10.8, 'fi': 10.4, 'nb': 9.6, 'sq': 11.9, 'fa': 10.4, 'lt': 9.6, 'et': 10.0, 'eo': 9.6, 'de': 9.2, 'lv': 10.4, 'so': 10.4, 'hi': 15.0, 'ca': 10.8, 'el': 11.5, 'be': 11.5, 'ga': 9.2, 'tl': 10.4, 'he': 8.5, 'sl': 10.0, 'ko': 30.0, 'ka': 11.5, 'la': 7.3, 'tr': 10.4, 'th': 12.7, 'hbs': 16.2, 'ar': 11.9, 'cs': 10.8, 'bn': 9.2, 'id': 10.0, 'te': 9.6, 'hu': 9.2, 'da': 10.0, 'mn': 15.8, 'mt': 10.4, 'es': 10.0, 'sk': 10.4, 'pl': 10.4, 'az': 13.1, 'af': 11.5, 'fr': 10.0, 'kk': 13.1, 'kn': 10.4, 'ne': 14.6, 'tt': 14.6, 'sv': 9.6, 'is': 10.4, 'pt': 11.2, 'it': 10.8, 'hy': 15.4, 'uk': 10.4, 'ms': 17.3, 'pa': 12.7, 'cy': 8.8, 'my': 13.5, 'ta': 11.2, 'bg': 10.8, 'ky': 10.4, 'nn': 10.8, 'ur': 11.5, 'eu': 10.0, 'si': 11.2, 'gu': 10.8, 'nl': 9.2, 'ps': 10.8, 'uz': 11.9, 'ro': 11.5, 'ml': 8.5, 'gl': 11.5, 'sw': 13.1, 'mk': 10.8}
# SEMIBAD 10 min 30 max
PERCENT_NUMBERS_DESIRED = {"standard": 1.2, 'en': 1.1 , 'ru': 1.4 , 'vi': 1.3 , 'ja': 2.7 , 'zh': 3.9 , 'mr': 1.0, 'fi': 1.1, 'nb': 1.1, 'sq': 1.1, 'fa': 1.1, 'lt': 1.3, 'et': 1.1, 'eo': 1.5, 'de': 1.1, 'lv': 1.3, 'so': 1.0, 'hi': 0.8, 'ca': 1.4, 'el': 1.2, 'be': 1.4, 'ga': 1.0, 'tl': 1.3, 'he': 1.6, 'sl': 1.2, 'ko': 3, 'ka': 1.2, 'la': 1.3, 'tr': 1.0, 'th': 0.5, 'hbs': 1.4, 'ar': 1.0, 'cs': 1.3, 'bn': 0.7, 'id': 1.0, 'te': 1.5, 'hu': 1.3, 'da': 1.2, 'mn': 1.3, 'mt': 2.6, 'es': 1.0, 'sk': 1.2, 'pl': 1.1, 'az': 1.2, 'af': 1.5, 'fr': 1.4, 'kk': 1.2, 'kn': 1.1, 'ne': 0.6, 'tt': 1.7, 'sv': 0.9, 'is': 0.9, 'pt': 1.3, 'it': 1.2, 'hy': 1.3, 'uk': 1.3, 'ms': 1.7, 'pa': 0.9, 'cy': 1.3, 'my': 0.3, 'ta': 1.1, 'bg': 1.3, 'ky': 1.2, 'nn': 1.2, 'ur': 0.8, 'eu': 1.2, 'si': 1.4, 'gu': 1.0, 'nl': 1.0, 'ps': 0.8, 'uz': 2.0, 'ro': 1.3, 'ml': 1.3, 'gl': 1.0, 'sw': 1.1, 'mk': 1.0}



## _____ BIG SEGMENTS SCORING _______________________________________________________________________________________________________________
BIG_TEXT_MIN = {"standard": 250, 'en': 232, 'ru': 186.0, 'vi': 203.0, 'ja': 100.0, 'zh': 70.0, 'mr': 247.0, 'fi': 243.0, 'nb': 243.0, 'sq': 240.0, 'fa': 243.0, 'lt': 230.0, 'et': 240.0, 'eo': 214.0, 'de': 240.0, 'lv': 227.0, 'so': 250.0, 'hi': 263.0, 'ca': 221.0, 'el': 237.0, 'be': 217.0, 'ga': 250.0, 'tl': 230.0, 'he': 208.0, 'sl': 234.0, 'ko': 100.0, 'ka': 234.0, 'la': 230.0, 'tr': 250.0, 'th': 289.0, 'hbs': 217.0, 'ar': 250.0, 'cs': 230.0, 'bn': 273.0, 'id': 247.0, 'te': 214.0, 'hu': 230.0, 'da': 237.0, 'mn': 230.0, 'mt': 133.0, 'es': 250.0, 'sk': 237.0, 'pl': 240.0, 'az': 237.0, 'af': 214.0, 'fr': 217.0, 'kk': 234.0, 'kn': 240.0, 'ne': 283.0, 'tt': 198.0, 'sv': 257.0, 'is': 257.0, 'pt': 230.0, 'it': 237.0, 'hy': 224.0, 'uk': 224.0, 'ms': 201.0, 'pa': 257.0, 'cy': 230.0, 'my': 305.0, 'ta': 240.0, 'bg': 227.0, 'ky': 234.0, 'nn': 237.0, 'ur': 263.0, 'eu': 237.0, 'si': 217.0, 'gu': 250.0, 'nl': 253.0, 'ps': 266.0, 'uz': 178.0, 'ro': 230.0, 'ml': 224.0, 'gl': 253.0, 'sw': 240.0, 'mk': 250.0}
BIG_TEXT_MAX = {"standard": 1000, 'en': 929.0, 'ru': 743.0, 'vi': 812.0, 'ja': 400.0, 'zh': 280.0, 'mr': 985.0, 'fi': 970.0, 'nb': 970.0, 'sq': 954.0, 'fa': 970.0, 'lt': 909.0, 'et': 954.0, 'eo': 833.0, 'de': 954.0, 'lv': 893.0, 'so': 1000.0, 'hi': 1061.0, 'ca': 863.0, 'el': 939.0, 'be': 848.0, 'ga': 1000.0, 'tl': 909.0, 'he': 802.0, 'sl': 924.0, 'ko': 300.0, 'ka': 924.0, 'la': 909.0, 'tr': 1000.0, 'th': 1183.0, 'hbs': 848.0, 'ar': 1000.0, 'cs': 909.0, 'bn': 1107.0, 'id': 985.0, 'te': 833.0, 'hu': 909.0, 'da': 939.0, 'mn': 909.0, 'mt': 452.0, 'es': 1000.0, 'sk': 939.0, 'pl': 954.0, 'az': 939.0, 'af': 833.0, 'fr': 848.0, 'kk': 924.0, 'kn': 954.0, 'ne': 1152.0, 'tt': 757.0, 'sv': 1030.0, 'is': 1030.0, 'pt': 909.0, 'it': 939.0, 'hy': 878.0, 'uk': 878.0, 'ms': 772.0, 'pa': 1030.0, 'cy': 909.0, 'my': 1259.0, 'ta': 954.0, 'bg': 893.0, 'ky': 924.0, 'nn': 939.0, 'ur': 1061.0, 'eu': 939.0, 'si': 848.0, 'gu': 1000.0, 'nl': 1015.0, 'ps': 1076.0, 'uz': 665.0, 'ro': 909.0, 'ml': 878.0, 'gl': 1015.0, 'sw': 954.0, 'mk': 1000.0}
DESIRED_BIG_TEXTS = 10
# Number of texts that means a 10 score


## _____ CHARS DETECTION _______________________________________________________________________________________________________________
BAD_CHARS = ["0021-002F", "003A-0040", "005B-0060", "007B-007E", "00A1-00BF", "02B0-0385", "0483-0489", "0559-055F", "0589-05C7", "0600-061F", "066A-066D", "06D4-06ED", "0700-070F", "1360-1368", "1800-180A", "1AB0-1AFF", "1C78-1C7F", "1CC0-1CC7", "1FBD-1FC1", "1FCD-1FCF", "1FDD-1FDF", "1FED-1FEF", "1FFD-2C5F", "2DE0-2E5D", "3000-303F", "3200-33FF", "4DC0-4DFF", "A670-A67F", "A6F0-A6F7", "FE10-FE6F",  "FF01-FF0F", "FF1A-FF20", "FF3B-FF40", "FF5B-FF65", "FFE0-FFFF", "1D100-1D1FF", "1F000-1FFFF"]
NUMBERS = ["0030-0039", "0660-0669", "06F0-06F9", "0964-096F", "09F2-09F9", "0B66-0B77", "0BE6-0BFA", "0C66-0C6F", "0C78-0C7E", "0CE6-0CEF", "0D66-0D79", "0DE6-0DEF", "0E50-0E5B", "0EC0-0ED9", "1040-1049", "1090-1099", "1369-137C", "17E0-17E9", "1810-1819", "19D0-19DA", "1A80-1A99", "1B50-1B59", "1C40-1C49", "1C50-1C59", "A830-A839", "A8D0-A8D9", "AA50-AA59"]
SPACES = ["0000-0020", "007F-00A0", "2B7E-2B7E", "008A-008A", "0088-0088"]
# Regex unicode codes for char-type count

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
bad_chars_pattern = join_utf_blocks(BAD_CHARS)
alpha_pattern = join_utf_blocks(BAD_CHARS + NUMBERS + SPACES, inverse=True)
#alphabetic chars are considered by elimination
spaces_pattern = join_utf_blocks(SPACES)



## _____ VALORATION FUNCTIONS _______________________________________________________________________________________________________________
def valorate_lang(ref_language, lang_segments, scores_lang, good_chars):
    if len(lang_segments) != len(scores_lang) or len(scores_lang) != len(good_chars):
        return -1000 #Errors from unmatched scores
    menu_length = MENUS_AVERAGE_LENGTH[ref_language] if ref_language in MENUS_AVERAGE_LENGTH else MENUS_AVERAGE_LENGTH["standard"]
    language_bias = LANG_DET_FIX[ref_language] if ref_language in LANG_DET_FIX else LANG_DET_FIX['standard']
    correct_lang_chars = 0
    correct_lang_chars_score = 0
    wrong_lang_chars = 0
    for n in range(len(lang_segments)):
        if good_chars[n] <= menu_length:
            continue
        elif lang_segments[n] == ref_language:
            rescaled_language_score = round((scores_lang[n] / language_bias * LANG_FIX_MEANING ), 1) if ref_language in LANG_DET_FIX else scores_lang[n]
            correct_lang_chars += good_chars[n]
            correct_lang_chars_score += good_chars[n] * rescaled_language_score
        else:
            wrong_lang_chars += good_chars[n] * scores_lang[n]

    if correct_lang_chars == 0:
        return 0
    results = (correct_lang_chars_score / (correct_lang_chars + wrong_lang_chars)*10)
    return round(results, 1) if results <= 10 else 10

def valorate_urls(ref_language, document, all_chars):
    url_admissible = URL_ADMISSIBLE[ref_language] if ref_language in URL_ADMISSIBLE else URL_ADMISSIBLE["standard"]
    url_max = URL_MAX[ref_language] if ref_language in URL_MAX else URL_MAX["standard"]
    url_quantity = max([document.count("www."), document.count("http")])
    url_quantity = url_quantity/all_chars
    url_quantity = url_max if url_quantity > url_max else url_quantity
    if url_quantity <= url_admissible:
        min_value = url_admissible
        max_value = 0
        min_range = 5
        max_range = 10
    else:
        min_value = url_max
        max_value = url_admissible -0.001
        min_range = 0
        max_range = 5-0.001
    return round(((url_quantity - min_value) / (max_value - min_value) * (max_range - min_range) + min_range), 2)

def valorate_bad_chars(ref_language, all_chars, ugly_chars):
    #30-15 BAD, 10-15 SEMIBAD, 1-10 GOOD, 0.8-1 SEMIBAD, 0.8-0 BAD
    percent_bad = PERCENT_BAD_CHARS_BAD[ref_language] if ref_language in PERCENT_BAD_CHARS_BAD else PERCENT_BAD_CHARS_BAD["standard"]
    percent_semibad = PERCENT_BAD_CHARS_SEMIBAD[ref_language] if ref_language in PERCENT_BAD_CHARS_SEMIBAD else PERCENT_BAD_CHARS_SEMIBAD["standard"]
    percent_max = PERCENT_BAD_CHARS_MAX[ref_language] if ref_language in PERCENT_BAD_CHARS_MAX else PERCENT_BAD_CHARS_MAX["standard"]
    percent_desired_min = PERCENT_BAD_CHARS_DESIRED_MIN[ref_language] if ref_language in PERCENT_BAD_CHARS_DESIRED_MIN else PERCENT_BAD_CHARS_DESIRED_MIN["standard"]
    percent_desired_max = PERCENT_BAD_CHARS_DESIRED_MAX[ref_language] if ref_language in PERCENT_BAD_CHARS_DESIRED_MAX else PERCENT_BAD_CHARS_DESIRED_MAX["standard"]

    bad_chars_ratio = round((ugly_chars/all_chars)*100, 1)
    if bad_chars_ratio >= percent_desired_min and bad_chars_ratio <= percent_desired_max:
        return 10.0
    elif bad_chars_ratio >= percent_bad[0]:
        bad_chars_ratio = percent_max if bad_chars_ratio > percent_max else bad_chars_ratio
        min_value = percent_max
        max_value = percent_bad[0]
        min_range = 0.0
        max_range = 4.999
    elif bad_chars_ratio >= percent_semibad[0]:
        min_value = percent_semibad[0]
        max_value = percent_bad[0] - 0.001
        min_range = 5.0
        max_range = 6.999
    elif bad_chars_ratio > percent_desired_max:
        min_value = percent_semibad[0]
        max_value = percent_desired_max
        min_range = 7.0
        max_range = 10.0
    elif bad_chars_ratio >= percent_semibad[1]:
        min_value = percent_semibad[1]
        max_value = percent_desired_min - 0.001
        min_range = 5.0
        max_range = 9.99
    else:
        min_value = 0.0
        max_value = percent_semibad[1] -0.001
        min_range = 0.0
        max_range = 4.999
        
    return round(((bad_chars_ratio - min_value) / (max_value - min_value) * (max_range - min_range) + min_range), 1)

def valorate_numbers(ref_language, good_chars, numbers):
    percent_max = PERCENT_NUMBERS_MAX[ref_language] if ref_language in PERCENT_NUMBERS_MAX else PERCENT_NUMBERS_MAX["standard"]
    percent_bad = PERCENT_NUMBERS_BAD[ref_language] if ref_language in PERCENT_NUMBERS_BAD else PERCENT_NUMBERS_BAD["standard"]
    percent_semibad = PERCENT_NUMBERS_SEMIBAD[ref_language] if ref_language in PERCENT_NUMBERS_SEMIBAD else PERCENT_NUMBERS_SEMIBAD["standard"]
    percent_desired = PERCENT_NUMBERS_DESIRED[ref_language] if ref_language in PERCENT_NUMBERS_DESIRED else PERCENT_NUMBERS_DESIRED["standard"]
    numbers_ratio = round((numbers/good_chars)*100, 1)
    if numbers_ratio <= percent_desired:
        return 10.0
    elif numbers_ratio >= percent_bad:
        numbers_ratio = percent_max if numbers_ratio > percent_max else numbers_ratio
        min_value = percent_max
        max_value = percent_bad
        min_range = 0.0
        max_range = 4.999
    elif numbers_ratio >= percent_semibad:
        min_value = percent_semibad
        max_value = percent_bad - 0.001
        min_range = 5.0
        max_range = 6.999
    else:
        min_value = percent_semibad
        max_value = percent_desired + 0.001
        min_range = 7.0
        max_range = 10.0
    return round(((numbers_ratio - min_value) / (max_value - min_value) * (max_range - min_range) + min_range), 1)

def valorate_spam(ref_language, document):
    menu_length = MENUS_AVERAGE_LENGTH[ref_language] if ref_language in MENUS_AVERAGE_LENGTH else MENUS_AVERAGE_LENGTH["standard"]
    spam = [segment for segment in document.split("\n") if len(segment) >= menu_length]
    if spam:
        spam = (len(spam) - len(list(set(spam))))/len(spam)*10
        return round((spam - 10) / - 10 * 10 , 1)
    else:
        return 10

def valorate_big_texts(ref_language, length_segments, lang_segments):
    if len(length_segments) != len(lang_segments):
        return (-1000, -1000)
    
    big_text_min = BIG_TEXT_MIN[ref_language] if ref_language in BIG_TEXT_MIN else BIG_TEXT_MIN["standard"]
    big_text_max = BIG_TEXT_MAX[ref_language] if ref_language in BIG_TEXT_MAX else BIG_TEXT_MAX["standard"]

    big_segments = []
    for n in range(len(length_segments)):
        if lang_segments[n] == ref_language and length_segments[n] > big_text_min:
            useful_chars = big_text_max if length_segments[n] > big_text_max else length_segments[n]
            score = round((useful_chars - big_text_min) / (big_text_max - big_text_min) * 10 , 1)
            big_segments.append(score)
                
    n_segments = len(big_segments) if len(big_segments) <= 10 else 10
    highter_segments = [x for x in big_segments if x >  5]
    score_very_big_segments = 0.0
    if highter_segments:
        score_very_big_segments = (sum(highter_segments)+0.1*(len(highter_segments)))/len(highter_segments)
        
    score_n_segments = round(n_segments / DESIRED_BIG_TEXTS * 10, 2)
    return (score_n_segments, score_very_big_segments)



## _____ MAIN SCORING FUNCTION _______________________________________________________________________________________________________________
def valorate_text(ref_lang, lang_segments, scores_lang, document):
    ling_bad_num_total = [(len(re.findall(alpha_pattern, segment)), len(re.findall(bad_chars_pattern, segment)), 
                    len(re.findall(numbers_pattern, segment))) for segment in document.split("\n")]
    good_chars = [x[0] for x in ling_bad_num_total]
    all_chars = sum(sum([x[0], x[1], x[2]]) for x in ling_bad_num_total)
    language_score = valorate_lang(ref_lang, lang_segments, scores_lang, good_chars)
    url_score = valorate_urls(ref_lang, document, all_chars)
    bad_chars_score = valorate_bad_chars(ref_lang, all_chars, sum(x[1] for x in ling_bad_num_total))
    numbers_score = valorate_numbers(ref_lang, sum(good_chars), sum(x[2] for x in ling_bad_num_total))
    spam_score = valorate_spam(ref_lang, document)
    big_segments_scores = valorate_big_texts(ref_lang, good_chars, lang_segments)
        
    score = (((language_score*0.4+6) * (url_score/10) * (bad_chars_score/10) * (numbers_score/10) * (spam_score/10)))*0.9 + (big_segments_scores[0]/10) + (big_segments_scores[1]/10)
    return [round(score, 1) if score <= 10 else 10, round(language_score, 1), round(url_score, 1), round(bad_chars_score, 1), round(numbers_score, 1), round(spam_score, 1), round(big_segments_scores[0], 1), round(big_segments_scores[1], 1)]



input_path=args['--input']
if( not os.path.exists(input_path)):
    print(f"File {input_path} not found")
    sys.exit(-1)

output_path=args['--output']
if( not os.path.exists(output_path)):
    print(f"Directory {output_path} not found")
    sys.exit(-1)

for json_f in os.listdir(input_path):
    if json_f.endswith(".jsonl"):
        documents = os.path.join(input_path, json_f)
        file_name = os.path.splitext(os.path.basename(json_f))[0]
        writing_path = os.path.join(output_path, f"{file_name}.csv")
        df = pd.DataFrame(columns=["score"])

        i = 0
        print(f"Processing: {file_name}")
        with open(documents, "r", encoding="utf-8") as file:
            n_lines = sum(1 for _ in file)
            print(f"{file_name} - {n_lines} documents")
        with open(documents, "r", encoding="utf-8") as file:
            for document in file:
                document = json.loads(document)
                score = valorate_text(ref_lang=document["document_lang"], lang_segments=document["langs"], scores_lang=document["scores"], document=document["text"])
                df.loc[document["id"]] = [score]
                
                i+=1
                if i % 10000 == 0:
                    print(f"{document['document_lang']} - {i}/{n_lines}")
            
        df["qualification_score"] = df.score.apply(lambda x: x[0])
        df["language_score"] = df.score.apply(lambda x: x[1])
        df["url_score"] = df.score.apply(lambda x: x[2])
        df["bad_chars_score"] = df.score.apply(lambda x: x[3])
        df["numbers_score"] = df.score.apply(lambda x: x[4])
        df["spam_score"] = df.score.apply(lambda x: x[5])
        df["n_big_segments_score"] = df.score.apply(lambda x: x[6])
        df["great_segment_score"] = df.score.apply(lambda x: x[7])
        df.to_csv(writing_path)
        print(f"Saved results in '{writing_path}'")