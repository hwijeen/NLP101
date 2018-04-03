
class Node():
    def __init__(self, elem, morph=None, isMorph=False):
        self.elem = elem       # 음소
        self.morph = ""     # 이 노드까지 포함해서 만든 형태소
        self.isMorph = False
        self.sibling = None
        self.children = None

class Trie():
    def __init__(self):
        self.head = Node(None, None)

    def add_node(self, morph):

        curr_node = self.head
        # morph = '나/NP'
        word, pos = morph.split('/')
        for phoneme in word:
            while curr_node.elem != phoneme:
                if curr_node.sibling:

                elif phoneme == word[-1]:
                    curr_node.sibling = Node(phoneme, morph, True)
                else:
                    curr_node.sibling = Node(phoneme)
                curr_node = curr_node.sibling

            if phoneme == word[-1]:
                curr_node = Node(phoneme)
            else:
                curr_node = Node(phoneme)


            if morph not in curr_node.children:
                curr_node.children[morph] = Node(phoneme, morph)
                if phoneme == word[-1]:
                    curr_node.children[morph].isMorph = True
            curr_node = curr_node.children[morph]


    # return possible morphs starting with the given prefix
    def lookup(self, morph):
        curr_node = self.head

        list = [morph.split('/')[0] for morph in curr_node.children.keys]
        if morph in :
            return
        else: return None



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
    print("head nodes :", trie.head.children['나/VV'].morph)
    trie.lookup("나")

    # input.txt에서 글을 불러오고
    # 문장을 어절 단위로 쪼개고
    # 어절에 대해서 TRIE이용 형태소 탐색 실시
    # Tabular parsing input 단위도 어절

    # Tabular parsing의 재귀식 찾기

    # trie.head.children에 dictionary 형태로 첫 음절들 모여있음
