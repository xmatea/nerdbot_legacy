import re
def format(args: str, flag_list: tuple, clearWhiteSpace: bool=True):
    formatted = {}

    if clearWhiteSpace:
        args = args.replace(' ', '')

    for flag in flag_list:
        regex = f"{flag}(.*?)({'|'.join(flag_list)}|$)"
        match = re.match(regex, args)
        if not match:
            break
        formatted.update({flag: match.group(1)})
    return formatted
