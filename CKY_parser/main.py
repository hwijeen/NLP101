from collections import defaultdict

from CKYParser import CKYParser

def get_grammar(grammar_path):
    unary_grammar = {}
    binary_grammar= defaultdict(list)
    full_lexicon = defaultdict(list)
    with open(grammar_path, 'r', encoding='utf-8-sig') as f:    # -sig to delete \ufeff
        grammar, lexicon = f.read().split("\n\n")

        grammar = grammar.split("\n")
        for line in grammar:
            num_RHS = len(line.split("->")[1].strip().split(' '))
            if num_RHS==2:
                LHS = line.split("->")[0].strip()
                RHS = (line.split("->")[1].strip().split(' ')[0], line.split("->")[1].strip().split(' ')[1])
                binary_grammar[LHS].append(RHS)    # {"NP": [("DT","NP"), ("NP", "PP")]}
            elif num_RHS==1:
                LHS = line.split("->")[1].strip()
                RHS = line.split("->")[0].strip()
                unary_grammar[LHS] = RHS    # {"det" : "DT"} the other way around!

        lexicon = lexicon.split("\n")
        for line in lexicon:
            LHS = line.split("->")[0].strip()
            RHS = line.split("->")[1].strip()
            full_lexicon[RHS].append(LHS)    # {"time" : "n","v"}

        return unary_grammar, binary_grammar, full_lexicon

def get_lines(input_path):
    with open(input_path, 'r', encoding='utf-8-sig') as f:
        lines = [line.strip().replace(".","") for line in f.readlines()]    # delete punctuation
        return lines

if __name__=="__main__":
    grammar_path = "grammar.txt"
    input_path = "input.txt"

    unary_grammar, binary_grammar, lexicon = get_grammar(grammar_path)
    lines = get_lines(input_path)

    parser = CKYParser(unary_grammar, binary_grammar, lexicon)
    for line in lines:
        parser.parse(line)




    ### FOR TEST ###
    # print("\n\n====TEST====")
    # print(len(unary_grammar), unary_grammar)
    #print(len(binary_grammar), binary_grammar)
    # print(len(lexicon), lexicon)
    # print(lines)
