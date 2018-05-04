import math

def isline(line):
        if '.' not in line: return False
        if line == "": return False
        if line =="\n": return False
        return True

class HMM():
    def __init__(self, path):
        self.path = path
        self.lines = []
        self.pos_len = 0
        self.pos_idx = {}
        self.word_len = 0
        self.word_idx = {}
        self.transMatrix = None 
        self.emitMatrix = None

        self.preprocess()

    def get_posLines(self, lines):

        unique_pos = set(['<s>','</s>'])

        pos_lines = []
        for line in lines:
            pos_line = ['<s>']
            chunks = line.split('+')
            for chunk in chunks:
                _, pos = chunk.split('/')
                unique_pos.add(pos)
                pos_line.append(pos)
            pos_line.append('</s>')
            pos_lines.append(pos_line)

        # len needed to initialize transition matrix
        self.pos_len = len(unique_pos)
        for idx, pos in enumerate(unique_pos):
            self.pos_idx[pos] = idx
        return pos_lines

    def get_emitLines(self, lines):

        unique_words= set()

        emit_lines = []
        for line in lines:
            emit_lines.append(line.split('+'))

        for line in emit_lines:
            for chunk in line:
                word, _ = chunk.split('/')
                unique_words.add(word)

        self.word_len = len(unique_words)
        for ix, word in enumerate(unique_words):
            self.word_idx[word] = ix
        return emit_lines

    def preprocess(self):
        with open(self.path, "r", encoding="EUC-KR") as f:
            for line in f:
                if isline(line):
                    line = line.split()[-1].strip()
                    self.lines.append(line)

    def make_bigram(self, pos_lines):
        pos_bigrams = []
        for pos_line in pos_lines:
            bigram = list(zip(pos_line[:-1], pos_line[1:]))
            pos_bigrams.append(bigram)
        return pos_bigrams

    def compute_transition(self):
        pos_lines = self.get_posLines(self.lines)
        self.transMatrix = [[0 for _ in range(self.pos_len)] for _ in range(self.pos_len)]

        # make bigram
#        pos_bigrams = []
#        for pos_line in pos_lines:
#            bigram = list(zip(pos_line[:-1], pos_line[1:]))
#            pos_bigrams.append(bigram)
        pos_bigrams = self.make_bigram(pos_lines)

        # make bigram count matrix
        for pos_bigram in pos_bigrams:
            for pre, post in pos_bigram:
                self.transMatrix[self.pos_idx[pre]][self.pos_idx[post]] += 1

        # add 1 smoothing
        self.transMatrix = [[elem+1 for elem in row] for row in self.transMatrix]

        # normalize to get probablity
        for ix, row in enumerate(self.transMatrix):
            denom = sum(row)
            self.transMatrix[ix] = [elem/denom for elem in row]

    def compute_observation(self):
        emit_lines = self.get_emitLines(self.lines)
        self.emitMatrix = [[0 for _ in range(self.word_len)] for _ in range(self.pos_len)]

        for line in emit_lines:
            for chunk in line:
                word, pos = chunk.split('/')
                self.emitMatrix[self.pos_idx[pos]][self.word_idx[word]] += 1

        # add 1 smoothing
        self.emitMatrix = [[elem + 1 for elem in row] for row in self.emitMatrix]
    
        # normalize to get probablity
        for ix, row in enumerate(self.emitMatrix):
            denom = sum(row)
            self.emitMatrix[ix] = [elem / denom for elem in row]

    def train(self):
        self.compute_transition()
        self.compute_observation()

    def predict(self,sentence):
        print(self.transMatrix[self.pos_idx['NNG']][self.pos_idx['JX']])

        lines_prob = []
        pos_lines = self.get_posLines(sentence)
        pos_bigrams = self.make_bigram(pos_lines)
        for pos_bigram in pos_bigrams:
            prob = 1
            for pre, post in pos_bigram:
                prob += math.log(self.transMatrix[self.pos_idx[pre]][self.pos_idx[post]])
            lines_prob.append(prob)

        emit_lines = self.get_emitLines(sentence)
        for ix, line in enumerate(emit_lines):
            for chunk in line:
                word, pos = chunk.split('/')
                lines_prob[ix] += math.log(self.emitMatrix[self.pos_idx[pos]][self.word_idx[word]])
        print(lines_prob)
        print(max(lines_prob))
        max_idx = lines_prob.index(max(lines_prob))
        print(sentence[max_idx])
    """
        prob_lines = []
        # compute transition prob
        for line in self.pos_bigrams:
            prob_line = 1
            for pre, post in line:
                prob_line *= math.log(self.transMatrix[self.pos_idx[pre]][self.pos_idx[post]])
            prob_lines.append(prob_line)

        # compute observation prob
        for ix, line in enumerate(self.emit_lines):
            for chunk in line:
                 word, pos = chunk.split('/')
                 prob_lines[ix] *= math.log(self.emitMatrix[self.pos_idx[pos]][self.word_idx[word]])
        max_idx = prob_lines.index(max(prob_lines)

        print(self.lines[max_idx])
       ### check if this implementation is correct
    """

