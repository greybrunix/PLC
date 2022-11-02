import re
import sys

def conv_csm_json(content, headers):
    # SECTION 1 - Preamble
    new = re.sub(r'([A-Za-z ]*)\n',r'\1',content)
    new = re.split(r',',new); # NOTE separates content by commas
    json_object = ""; tmp_array = {}
    tmp_head = headers.copy(); # NOTE safeguarding the headers list
    flag = 0; i = 0


    # SECTION 2 - List SEARCHING
    # A for does not provide enough control
    while i < (len(tmp_head)-1):
        if tmp_head[i] == tmp_head[i+1]: # NOTE we found a list
            flag = 1; test = str(headers[i]); tmp_array[headers[i]] = []
        while flag == 1:
            if test not in tmp_head:
                # This is due to removing from tmp_head
                flag = 0
                new.insert(i,tmp_array[test])
                tmp_head.insert(i,test)
            if flag == 1:
                tmp_head.pop(i)
                try:
                    tmp_array[test].insert(i,float(new.pop(i)))
                except ValueError:
                    tmp_array[test].insert(i,new.pop(i))
        i= i+1; # NOTE iterate the rest of the content

    
    # SECTION 3 - Writing to buffer
    for i, v in zip(tmp_head[:-1], new[:-1]):
        if isinstance(v,list):
            json_object += "\t\""+i+""+"\": " +str(v)+",\n\t"
        else:
            json_object += "\t\""+i+""+"\": \""+str(v)+"\",\n\t"
    # NOTE final element
    if isinstance(new[-1], list):
        json_object += "\t\""+tmp_head[-1]+"\": "+ str(new[-1])+"\n\t"
    else:
        json_object += "\t\""+tmp_head[-1]+"\": \""+str(new[-1])+"\"\n\t"
    

    return json_object

def main():

    agrev_func = {'AVG', 'SUM', 'COUNT', 'MAX', 'MIN'}

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
    tst = re.findall(r'([A-Za-z0-9 \_\-]+){([0-9]+)(,[0-9]+)?}(::[A-Z]+)?',headers) 
    matches_list = []
    if tst:
        for x in tst:
            headers = re.subn(r'(?<=,)(?=,)|(?<=},)(?=,)|(?<=,,)(?=)',
                            x.group(1),
                            headers,
                            count=int(x.group(2))
                            )
            matches_list.append(x)
        headers = re.split(r',', headers[0])
        for x in matches_list:
            headers.remove(x.group())
    else:
        headers = re.split(r',', headers)
    # NOTE considering only one list can be accepted
    # TODO maybe use findall to get all instances of list creations
    final = lines.pop(len(lines)-1)


    # SECTION 3 - Creating a buffer with JSON file and writing to it
    with open(file_name+'.json', 'w+') as f:
        f.write('[\n')
        for line in lines:
            js_object = "\t{\n\t"; js_object += conv_csm_json(line, headers)
            js_object += "},\n"; f.write(js_object)
        js_object = "\t{\n\t"; js_object += conv_csm_json(final, headers)
        js_object += "}\n]"; f.write(js_object); f.close()
    return 0

if __name__ == '__main__':
    main()

# TODO Lists with variable length (from x to y in size)
# TODO allowed agreg function, SUM, AVG, MAX, MIN # NOTE use evals
# NOTE already accepting base case, one single list in any position
# TODO multiple lists, lists with varying length and functions over lists
# TODO MAYBE subs
