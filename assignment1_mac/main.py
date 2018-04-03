from trie import Trie
from tabular_parser import TabularParser

def add_morph_rule(tokens, morph_rules):
    num_rule = len(morph_rules)
    for token in tokens:
        morphs = token.split('+')
        pos = [morph.split('/')[-1] for morph in morphs]
        for i in range(len(pos)-1):
            morph_rule = (pos[i], pos[i+1])
            if morph_rule not in morph_rules:
                morph_rules[morph_rule] = num_rule
                num_rule += 1
    return morph_rules

def get_morphs_from_text(path):
    file = open(path, encoding='utf-8')

    lines = [line.strip() for line in file.readlines()]

    morph_rules = {}
    morphs = []
    for line in lines:
        #if line == '': break
        tokens = line.split(' ')
        morph_rules = add_morph_rule(tokens, morph_rules)
        for token in tokens:
            morphs += token.split('+')
    return morphs, morph_rules

def get_lines(path):
    with open(path, encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines()]
    return lines

def get_tokens(line):
    return  line.split(" ")

if __name__ == "__main__":


    # Q2: build dictionary & grammar
    data_path = "./morph_rule.txt"

    trie = Trie()
    morphs, morph_rules = get_morphs_from_text(data_path)

    for morph in morphs:
        trie.add_node(morph)

    # Q3: Tabular parsing
    parser = TabularParser(trie, morph_rules)
    
    input_path = "./input.txt"
    lines = get_lines(input_path)
    
    for ix, line in enumerate(lines):
        print("\ninput sentence #%d: %s" % (ix+1, line))
        print("=====parsing result=====")
        tokens = get_tokens(line)
        for token in tokens:
            print(parser.parse(token))

    ### FOR TEST ###
#    print("##### TEST #####")
#    print(lines)
#    print("binary morph_rules: ", morph_rules)
#    print(trie.lookup("어머니는"))

