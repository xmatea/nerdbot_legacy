
def format(args: tuple, flag_list: tuple):
    formatted = {}
    for index, arg in enumerate(args):
        if arg in flag_list:
            i=1
            a=[]
            while i < len(args)-index+1 and not args[index+i] in flag_list:
                a.append(args[index+i])
                print(args[index+i])
                print(i)
                i+=1
            formatted.update({arg: a})
            print(formatted)
        return formatted
