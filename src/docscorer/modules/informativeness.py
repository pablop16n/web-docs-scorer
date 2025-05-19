import os
import joblib
import zstandard
import re

class Informativeness:
    def __init__(self, config_files):
        GROUP_A = {"Grek": "GROUP_A", "Latn": "GROUP_A", "Cyrl": "GROUP_A", "Hang": "GROUP_A", "Jpan": "GROUP_A"}
        GROUP_B = {"Deva": "GROUP_B", "Beng": "GROUP_B", "Telu": "GROUP_B", "Tibt": "GROUP_B", "Geor": "GROUP_B", "Gujr": "GROUP_B", "Khmr": "GROUP_B", "Knda": "GROUP_B", "Laoo": "GROUP_B", "Mlym": "GROUP_B", "Mymr": "GROUP_B", "Orya": "GROUP_B", "Sinh": "GROUP_B", "Taml": "GROUP_B", "Thai": "GROUP_B", "Olck": "GROUP_B"}
        GROUP_C = {"Arab": "GROUP_C", "Armn": "GROUP_C", "Ethi": "GROUP_C", "Guru": "GROUP_C", "Hebr": "GROUP_C"}
        GROUP_D = {"Hans": "GROUP_D", "Hant": "GROUP_D"}
        self.GROUPS = {**GROUP_A, **GROUP_B, **GROUP_C, **GROUP_D}
        FUNCTION_FILES = {"GROUP_A": "function_group_a.pkl", "GROUP_B": "function_group_b.pkl", "GROUP_C": "function_group_c.pkl", "GROUP_D": "function_group_d.pkl"}
        self.cctx = zstandard.ZstdCompressor()
        self.functions = {group: joblib.load(os.path.join(config_files, FUNCTION_FILES[group])) for group in FUNCTION_FILES}

        self.outsiders_function_fix = {"GROUP_A": 180000, "GROUP_B": 250000, "GROUP_C": 180000, "GROUP_D": 75000} #Since our data is not representative over these not compressed weights (x value in the charts), we stop the prediction function (line in the charts) in this point, in order to prevent irreal predictions, like more than 100% of compression rate, which is impossible. 

    def __rescale_rate(self, value, min_value, max_value, min_range, max_range):
        return round(((value - min_value) / (max_value - min_value) * (max_range - min_range) + min_range), 1)

    def __information_score(self, x_value, y_value, script_code):
        group = self.GROUPS[script_code] if script_code in self.GROUPS else "GROUP_A" #If script is not in the list, A group is for default

        x_value = self.outsiders_function_fix[group] if x_value > self.outsiders_function_fix[group] else x_value
        predict_compression_rate = self.functions[group]
        y_pred = float(predict_compression_rate(x_value))
        
        if y_value <= y_pred + 10 and y_value > y_pred - 10:
            return 10
        elif y_value >= y_pred + 20 or y_value <= y_pred - 20:
            return 0
        #way_down
        elif y_value < y_pred and y_value > y_pred - 15:
            return self.__rescale_rate(y_value, y_pred - 10, y_pred - 15, 10, 7)   
        elif y_value < y_pred and y_value > y_pred - 20:
            return self.__rescale_rate(y_value, y_pred - 15, y_pred - 20, 7, 0)
        #way_up
        elif y_value <= y_pred + 15:
            return self.__rescale_rate(y_value, y_pred + 10, y_pred + 15, 10, 7)
        elif y_value < y_pred + 20:
            return self.__rescale_rate(y_value, y_pred + 15, y_pred + 20, 7, 0)

    def rate_information(self, text, script_code):
        text = re.sub("\d", "1", text.lower())
        compressed_weight = len(self.cctx.compress(bytes(text, 'utf-8')))
        raw_weight = 1 if len(text.encode('utf-8')) == 0 else len(text.encode('utf-8'))
        compression = round((1 - compressed_weight / raw_weight) * 100, 1)
        return self.__information_score(raw_weight, compression, script_code)
