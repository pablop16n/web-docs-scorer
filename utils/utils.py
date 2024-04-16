def precision_round(number):
    number_str = str(number)
    first_digit_index = next((i for i, d in enumerate(number_str) if d != '0' and d != '.'), None)
    if first_digit_index != None:
        to_round_digits = max(0, 1 - first_digit_index)
        rounded_value = round(number, to_round_digits)
    else:
        rounded_value = round(number, 1)
    return rounded_value

def average(list):
    return precision_round(sum(list)/len(list))