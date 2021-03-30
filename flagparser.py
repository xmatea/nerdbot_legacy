import re
def format(args: str, flag_list: tuple, clearWhiteSpace: bool=True):
    formatted = {}

    # will clear whitespace ex: -range x=[2, 7] will be formatted as {'-range': 'x=[2,7]'}
    if clearWhiteSpace:
        print("aaa")
        args = args.replace(' ', '')

    for flag in flag_list:
        regex = f"{flag}(.*?)({'|'.join(flag_list)}|$)"
        match = re.match(regex, args)
        if not match:
            break
        formatted.update({flag: match.group(1)})
        print(formatted)
