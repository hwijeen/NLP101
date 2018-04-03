class Node():
    def __init__(self, elem):
        self.elem = elem
        self.pos = []
        self.word = None
        self.isMorph = False
        self.children = {}

    def add_pos_word(self, pos, word):
        self.pos.append(pos)
        self.word = word
        self.isMorph = True

    def get_tag(self):
        result = set([self.word + "/" + pos for pos in self.pos])
        return list(result)

class Trie():
    def __init__(self):
        self.head = Node(None)

    def add_node(self, morph):
        curr_node = self.head
        word, pos = morph.split('/')
        for phoneme in word:
            if phoneme not in curr_node.children:
                curr_node.children[phoneme] = Node(phoneme)
            curr_node = curr_node.children[phoneme]
        curr_node.add_pos_word(pos, word)

    def lookup(self, word):
        curr_node = self.head
        for phoneme in word:
            if phoneme in curr_node.children:
                curr_node = curr_node.children[phoneme]
            else: return []

        if curr_node.isMorph == True:
            return curr_node.get_tag()
        else:return []