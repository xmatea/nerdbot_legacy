def format(args: tuple, flag_list: tuple):
    formatted = {}
    print(args)
    for index, arg in enumerate(args):
        if arg in flag_list:
            i=1
            a=[]
            while i < len(args)-index and not args[index+i] in flag_list:
                a.append(args[index+i])
                i+=1
            formatted.update({arg: a})
        return formatted