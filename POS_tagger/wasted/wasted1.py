
class Node():
    def __init__(self, elem, morph=None):
        self.elem = elem       # 음소
        self.morph = morph     # 이 노드까지 포함해서 만든 형태소(가능할 경우)
        self.children = {}

class Trie():
    def __init__(self):
        self.head = Node(None)

    def add_node(self, morph):

        curr_node = self.head
        # morph = '나/NP'
        word, pos = morph.split('/')
        for phoneme in word:
            if phoneme not in curr_node.children:
                if phoneme == word[-1]:
                    curr_node.children[phoneme] = Node(phoneme, morph)
                else:
                    curr_node.children[phoneme] = Node(phoneme)
            # same phoneme, different pos
            elif pos != curr_node.children[phoneme].morph.split('/')[-1]:
                print("same phonemeㅠㅠ %s", phoneme)



            curr_node = curr_node.children[phoneme]


    # return possible morphs starting with the given prefix
    def starts_with(self, prefix):
        curr_node = self.head

        if prefix not in curr_node.children:
            raise Exception("prefix not in dictionary!")

        # possible_morphs=[]
        # while curr_node:
        #     if curr_node.morph:
        #         possible_morphs.append(curr_node.morph)
        #         curr_node = curr_node.children[]


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


if __name__ == "__main__":

    path = "./morph_rule.txt"
    file = open(path, encoding='utf-8')

    lines = [line.strip() for line in file.readlines()]

    morph_rules = {}
    trie = Trie()
    for line in lines:
        if line == '': break
        tokens = line.split(' ')
        morph_rules = add_morph_rule(tokens, morph_rules)
        for token in tokens:
            morphs = token.split('+')
            for morph in morphs:
                trie.add_node(morph)


    ### FOR TEST ###
    print("binary morph_rules: ", morph_rules)
    print("head nodes :", trie.head.children["나"].morph)
    #trie.print_morphs()

    # input.txt에서 글을 불러오고
    # 문장을 어절 단위로 쪼개고
    # 어절에 대해서 TRIE이용 형태소 탐색 실시
    # Tabular parsing input 단위도 어절

    # Tabular parsing의 재귀식 찾기

    # trie.head.children에 dictionary 형태로 첫 음절들 모여있음
