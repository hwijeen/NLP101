class TabularParser():
    def __init__(self, trie, morph_rules):
        self.trie = trie
        self.morph_rules = morph_rules
        self.table = [[]]    # return처리랑 차이?    # 이중 list 선언?

    def init_table(self, input):
        input_len = len(input)
        self.table = [[None for _ in range(input_len)] for _ in range(input_len)]
        for i in range(input_len):
            for j in range(input_len):
                if i<=j:
                    self.table[i][j] = self.trie.lookup(input[i:j+1])

    def grammar_check(self, morph1, morph2):
        pos1 = morph1.split('/')[1]
        pos2 = morph2.split('/')[1].split('+')[0]    # for items that have more than two elements
        if (pos1, pos2) in self.morph_rules: return True
        else: return False

    def merge(self, room1, room2):
        merged = []
        for morph1 in room1:
            for morph2 in room2:
                if self.grammar_check(morph1, morph2):
                    merged.append(morph1+'+'+morph2)
        return merged

    def parse(self, input):
        self.init_table(input)
        for i in range(len(input)):
            for j in range(1,i+1):
                for k in range(i-j,i):
                    self.table[i-j][i] += (self.merge(self.table[i-j][k],
                                self.table[k+1][i]))
        return self.table[0][len(input)-1]
        
