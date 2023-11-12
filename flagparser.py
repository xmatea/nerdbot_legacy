# Parses all flag arguments
import re

def format(args: str, flag_list: tuple, clearWhiteSpace: bool=True):
    formatted = {}

    if clearWhiteSpace:
        args = args.replace(' ', '')

    content = re.match(f"(.*?)({'|'.join(flag_list)}|$)", args)
    if content:
        formatted.update({'content': content.group(1)})

    for flag in flag_list:
        regex = f"(.*?){flag}(.*?)({'|'.join(flag_list)}|$)"
        match = re.match(regex, args)
        if match:
            formatted.update({flag: match.group(2)})
    return formatted
