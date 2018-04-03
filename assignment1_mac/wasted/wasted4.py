from collections import defaultdict

class Node():
    def __init__(self, elem, pos, word):
        self.elem = elem       # 음소
        self.pos = pos
        self.word = word     # 이 노드까지 포함해서 만든 형태소
        self.isMorph = False
        self.children = defaultdict(list)

class Trie():
    def __init__(self):
        self.head = Node(None, None, None)

    def add_node(self, morph):

        curr_node = self.head
        # morph = '나/NP'
        word, pos = morph.split('/')
        for phoneme in word:
            # 음절 같은 거 없을 때 걍 추가
            if phoneme not in curr_node.children:
                curr_node.children[phoneme].append(Node(phoneme, pos, word))
            # 음절 같은 거 있을 때
            else:
                for ix, item in enumerate(curr_node.children[phoneme]):
                    # 음절도 같고 품사도 같으면 타고 내려가고
                    if pos == item.pos:
                        curr_node = curr_node.children[phoneme][ix]
                        continue
                # 아니면 추가!
                curr_node.children[phoneme].append(Node(phoneme, pos, word))
            curr_node = curr_node.children[phoneme][-1]

        curr_node.isMorph = True

    def lookup(self, word):
        curr_node = self.head
        # word "나는"
        for phoneme in word:
            if phoneme in curr_node.children:
                for node in curr_node.children[phoneme]:
                    curr_node = node

            else:
                return None
        if curr_node.isMorph == True:
            return word + "/" + curr_node.pos


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

    trie.lookup("엄")

    ### FOR TEST ###
    print("binary morph_rules: ", morph_rules)
    print(len(trie.head.children["어"]))
    print(trie.head.children["어"][0].elem)
    print(trie.head.children["어"][0].pos)
    print(trie.head.children["어"][1].elem)
    print(trie.head.children["어"][1].pos)


    # input.txt에서 글을 불러오고
    # 문장을 어절 단위로 쪼개고
    # 어절에 대해서 TRIE이용 형태소 탐색 실시
    # Tabular parsing input 단위도 어절

    # Tabular parsing의 재귀식 찾기

    # trie.head.children에 dictionary 형태로 첫 음절들 모여있음
