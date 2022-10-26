import re

def conv_csm_json(content, headers):
    new = re.sub(r'([A-Za-z ]*)\n',r'\1',content); # NOTE removes newlines from content
    new = re.split(r',',new); # NOTE separates content by commas
    json_object = "";
    tmp_array = {};
    tmp_head = headers.copy(); # NOTE safeguarding the headers list
    flag = 0;
    i = 0;

    # NOTE loop that searches for lists
    while i < (len(tmp_head)-1): # NOTE a for would be unnecessary as it does not provide enough control
        if tmp_head[i] == tmp_head[i+1]: # NOTE we found a list
            flag  = 1;
            test = str(headers[i]);
            tmp_array[headers[i]] = [];
        while flag == 1:
            if test not in tmp_head: # NOTE since we are removing from the list we can do this
                flag = 0;
                new.insert(i,tmp_array[test]);
                tmp_head.insert(i,test);
            if flag == 1:
                tmp_head.pop(i);
                try: # NOTE we are accepting list values as either floats or anything else (strings)
                    tmp_array[test].insert(i,float(new.pop(i)));
                except ValueError:
                    tmp_array[test].insert(i,new.pop(i));
        i= i+1; # NOTE iterate the rest of the content

    # NOTE for loop that writes to the js object
    for i in range(0,len(tmp_head)-1):
        if (type(new[i]).__name__ == 'list'): # NOTE when handling a list, there are some changes to be made
            json_object += "\t\""+tmp_head[i]+""+"\": " +str(new[i])+",\n\t";
        else:
            json_object += "\t\""+tmp_head[i]+""+"\": \""+str(new[i])+"\",\n\t";
    # NOTE final element
    if (type(new[-1]).__name__ == 'list'):
        json_object += "\t\""+tmp_head[-1]+"\": "+ str(new[-1])+"\n\t";
    else:
        json_object += "\t\""+tmp_head[-1]+"\": \""+str(new[-1])+"\"\n\t";
    return json_object;

def main():

    with open('alunos.csv', 'r') as f:
        lines = f.readlines(); # NOTE Line by line seems more intuitive and easier to handle
        f.close();

    lines[0] = re.sub(r'([A-Za-z ]*)\n', r'\1', lines[0]); # NOTE removes new lines from headers
    headers = lines.pop(0);
    tst = re.search(r'([A-Za-z]+){([0-9]+)}',headers); # NOTE Considering List names contain only one word and only letters
    # NOTE group one is the name and group 2 is N
    if tst:
        headers = re.subn(r'(?<=,)(?=,)|(?<=},)(?=,)|(?<=,,)(?=)',tst.group(1),headers,count=(int(tst.group(2))));
        headers = re.split(r',', headers[0]); #NOT3 vai star a mudar o tipo do h3ad3rs
        headers.remove(tst.group()); # NOTE removes the list creation from the headers
    else:
        headers = re.split(r',', headers);
    # NOTE considering only one list can be accepted
    # TODO maybe use findall to get all instances of list creations
    final = lines.pop(len(lines)-1);

    with open('alunos.json', 'w') as f:
        f.write('[\n');
        for line in lines:
            js_object = "\t{\n\t";
            js_object += conv_csm_json(line, headers);
            js_object += "},\n";
            f.write(js_object);
        js_object = "\t{\n\t";
        js_object += conv_csm_json(final, headers);
        js_object += "}\n]";
        f.write(js_object);
        f.close();

    return 0;

if __name__ == '__main__':
    main();

# TODO Lists with variable length (from x to y in size)
# TODO allowed agreg function, SUM, AVG, MAX, MIN # NOTE use evals
# NOTE already accepting base case, one single list in any position
# TODO multiple lists, lists with varying length and functions over lists
# TODO MAYB3 subs
