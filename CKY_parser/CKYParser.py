class Node():
    def __init__(self, word, constituent, origin=None, origin_idx=(0,0)):
        self.word = word
        self.constituent = [constituent] if type(constituent) == str else constituent  # to prevent double list
        self.origin = origin
        self.origin_idx = origin_idx


class CKYParser():
    def __init__(self, unary_grammar, binary_grammar, lexicon):
        self.unary_grammar = unary_grammar
        self.binary_grammar = binary_grammar
        self.lexicon = lexicon
        self.table = [[]]  # is this necessary?

    def init_table(self, input):
        self.table = [[[] for _ in range(len(input))] for _ in range(len(input))]

        for i in range(len(input)):
            word = input[i]
            # constituent = [self.unary_grammar[pos] for pos in self.lexicon[word] if pos in self.unary_grammar]
            constituent = []
            for pos in self.lexicon[word]:
                print("%s -> %s" % (pos, word))  # assignment requirement
                if pos in self.unary_grammar:
                    print("%s -> %s" % (self.unary_grammar[pos], pos))
                    constituent.append(self.unary_grammar[pos])
            self.table[i][i].append(Node(word, constituent))  # list containing one node

    def grammar_check(self, constituent1, constituent2):
        for value in self.binary_grammar.values():
            if (str(constituent1), str(constituent2)) in value: return True
        else:
            return False

    def merge(self, word, node_list1, node_list2):
        merged = []
        if len(node_list1) == 0 or len(node_list2) == 0: return []  # returning empty list instead of None is important!!
        for node1 in node_list1:
            for node2 in node_list2:
                for ix1, constituent1 in enumerate(node1.constituent):
                    for ix2, constituent2 in enumerate(node2.constituent):
                        if self.grammar_check(constituent1, constituent2):
                            for merged_constituent, origin in self.binary_grammar.items():
                                if (constituent1, constituent2) in origin:
                                    print("%s -> %s %s" % (merged_constituent, constituent1, constituent2))  # requirement
                                    merged.append(Node(word, merged_constituent, (node1, node2), (ix1, ix2)))
        return merged

    def dfs(self, table, node, visited, output, idx):
        if node not in visited:
            visited.append(node)
            output += "(" + str(node.constituent[idx]) + " "  # which constituent?
            if type(node.word) == str: output += node.word
            if node.origin is None:  # leaf node
                output += ")"
                return visited, output
            for side, child in enumerate(node.origin):
                idx = node.origin_idx[side]
                visited, output = self.dfs(table, child, visited, output, idx)
            output += ")"
        return visited, output

    # printing tree with DFS
    def print_tree(self, input_len):
        possible_heads = [node for node in self.table[0][input_len - 1] if node.constituent == ['S']]
        for head in possible_heads:
            visited, output = self.dfs(self.table, head, [], "", 0)
            print(output)

    def parse(self, input):
        input = input.split(" ")  # unit: eojeol
        self.init_table(input)
        for i in range(len(input)):
            for j in range(i + 1):
                if i - j == i: continue
                for k in range(i - j, i):
                    self.table[i - j][i] += self.merge(input[i - j:i + 1], self.table[i - j][k],
                                                       self.table[k + 1][i])  # merge(Node_list1, Node_list2)
        print("\n=====printing parsed tree====")
        self.print_tree(len(input))
        print("\n\n")


