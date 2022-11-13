import re
import sys


# SECTION FOR AGGREGATION FUNCTIONS
def SUM(li):
    res = 0
    for el in li:
        res += el
    return res

def COUNT(li):
    return len(li)

def AVG(li):
    return SUM(li) // COUNT(li)

def MAX(li):
    res = li[0]
    for el in li:
        if el > res:
            res = el
    return res

def MIN(li):
    res = li[0]
    for el in li:
        if el < res:
            res = el
    return res

# FUNCTION THAT CREATES THE JSON FILE
def conv_csv_json(content, headers, flags):
    # SECTION 1 - Preamble
    new = re.sub(r'([A-Za-z ]*)\n',r'\1',content)
    new = re.split(r',',new); # NOTE separates content by commas
    json_object = ""; tmp_array = {}
    tmp_head = headers.copy(); # NOTE safeguarding the headers list
    flag = False; i = 0
    curr_check = 0
    flagM = False; flagAg = False; flagErr = False
    # NOTE flags meanings:
    # flag <- List has been found
    # flagM <- upper bound is M and not N
    # flagAg <- Aggregation function to be applied at end
    # flagErr <- Error was found
    patternreg = "\t\"qwe\": \"yui\",\n\t"
    patternlis = "\t\"asd\": hjk,\n\t"
    patternerg = "\t\"zxc\": \"nm,\"\n\t"
    patterneli = "\t\"123\": 789\n\t"

    # SECTION 2 - List SEARCHING
    # A for does not provide enough control
    if flags:
        while i < (len(tmp_head)-1) and not flagErr:
            if tmp_head[i] == tmp_head[i+1]: # NOTE we found a list
                flag = True; test = str(tmp_head[i]); tmp_array[test] = []
                N = int(flags[test][0])
                try:
                    if (flags[test][1]):
                        try:
                        # Checks if the list is of N,M format
                            M = int(flags[test][1])
                            flagM = True
                            try:
                            # Checks if the list has an agreg function
                                if flags[test][2]:
                                    agreg = re.sub(r'::([A-Z]+)',r'\1',
                                                  flags[test][2])
                                    flagAg = True
                            except IndexError:
                            # If there is no agreg function
                                agreg = ''
                                flagAg = False
                        except ValueError:
                        # There is an agreg function
                            M = N
                            agreg = re.sub(r'::([A-Z]+)',r'\1',
                                           flags[test][1])
                            flagM = False; flagAg = True
                except IndexError:
                    flagM = False; flagAg = False;
                    M = N; agreg = ''
            while flag and not flagErr:
                if (test not in tmp_head): 
                # NOTE that there must be spaces in varying size lists,
                # TRIVIAL implementation
                # NOTE This is due to removing from tmp_head
                    if flagAg:
                        try:
                            tmp_array[test] = eval(agreg+'('+
                                                  str(tmp_array[test])+')')
                        except SyntaxError:
                            flagErr = True
                    # Reset flags
                    flag = False; flagM = False; flagAg = False;
                    new.insert(i,tmp_array[test])
                    tmp_head.insert(i,test)
                    # Reset Values
                    curr_check = 0
                    del N; del M; del agreg; del elem_test
                if flag:
                    tmp_head.pop(i)
                    # Regular Search
                    if tmp_array[test]:
                            try:
                                elem_test = new.pop(i)
                                tmp_array[test].append(int(elem_test))
                            except ValueError:
                                if (curr_check == 0):
                                    curr_check = len(tmp_array[test])
                                if (flagM and elem_test == '' and
                                 curr_check >= N and 
                                curr_check <= M):
                                    curr_check += 1
                                else:
                                    flagErr = True
                # NOTE the try does remove the value from new
                # Thus it is safer to remove to a safe variable
                    else:
                        # Initial Search
                        try:
                            tmp_array[test].append(int(new.pop(i)))
                        except ValueError:
                            flagErr = True

            i= i+1; # NOTE iterate the rest of the content

    # SECTION 3 - Writing to buffer

    if not flagErr:
        for i, v in zip(tmp_head[:-1], new[:-1]):
            if (isinstance(v,list)):
                json_object += re.sub(r'asd\": hjk',
                                      r''+i+'\": '+str(v)+r'',
                                    patternlis,count=1)
            else:
                json_object += re.sub(r'qwe\": \"yui',
                                      r''+i+'\": \"'+str(v)+r'',
                                      patternreg,count=1)
        if (isinstance(new[-1],list)):
            json_object += re.sub(r'123\": 789',
                                  r''+tmp_head[-1]+'\": '+str(new[-1]),
                                  patterneli,count=1)
        else:
            json_object += re.sub(r'zxc\": \"nm,',
                                  r''+tmp_head[-1]+'\": \"'+str(new[-1])+r'',
                                  patternerg,count=1)
    else:
        raise ValueError
    return json_object


# MAIN FUNCTION
def main():

    # SECTION 1 - Getting the csv file
    file = input("Insert name of file:\n>> ")
    file_test = re.search(r'([A-Za-z0-9\_\-]+)\.csv',file)
    if not file_test:
        sys.exit("File is not a CSV file")
    file_name = file_test.group(1)
    del file_test
    # NOTE
    try:
        f = open(file, 'r')
    except OSError:
        raise OSError; exit(1)
        # NOTE tells the user the file doesn't exist
    lines = f.readlines(); f.close()

    # SECTION 2 - parsing lists
    lines[0] = re.sub(r'([A-Za-z ]*)\n', r'\1', lines[0])
    headers = lines.pop(0)
    tst = re.findall(r'([A-Za-z0-9 \_\-]+){([0-9]+)'
                     '(,([0-9]+))?}(::[A-Z]+)?',headers) 
# 'Notas{3,5}::AVG'
# (NOTAS) (3) '' '' ''
    matches_list = []
    flags = {}
    if tst:
        for x in tst:
            N = int(x[1])
            if (x[3]):
                N = int(x[3])
            headers = re.sub(r'(?<=\,)(?=\,)|'
                             '(?<=}\,)(?=\,)|(?<=\,\,)(?=)',
                            x[0],
                            headers,
                            count=N
                            )
            x = list(x)
            flags[x[0]] = []
            if x[1]: # N
                flags[x[0]].append(int(x[1]))
            if x[3]: # M
                flags[x[0]].append(int(x[3]))
            if x[-1]: # Function
                flags[x[0]].append(x[-1])
            x.insert(1,'{');x.insert(4,'}')
            x.pop(5)
            matches_list.append(''.join(x))
        headers = re.split(r'(?<!{\d),(?!\d})', headers)
        for x in matches_list:
            headers.remove(x) # List creation removed
    else:
        headers = re.split(r',', headers)
    final = lines.pop(len(lines)-1)

    # SECTION 3 - Creating a buffer with JSON file and writing to it
    with open(file_name+'.json', 'w+') as f:
        f.write('[\n')
        for line in lines:

            js_object = "\t{\n\t"
            try:
                js_object += conv_csv_json(line, headers, flags)
            except ValueError:
                sys.exit("Incorrectly made CSV file\n")
            js_object += "},\n"; f.write(js_object)
        js_object = "\t{\n\t"
        try:
            js_object += conv_csv_json(final, headers, flags)
        except ValueError:
            sys.exit("Incorrectly made CSV file\n")
        js_object += "}\n]"; f.write(js_object); f.close()
    return 0


# SCRIPT TO BE EXECUTED
if __name__ == '__main__':
    main()
