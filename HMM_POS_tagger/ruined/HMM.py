import math

class HMM():
    def __init__(self, path):
        self.path = path
        self.lines = []
        self.pos_lines = []      # needed?
        self.pos_len = 0
        self.pos_idx = {}
        self.pos_bigrams = []    # needed?
        self.emit_lines = []     # needed?
        self.word_len = 0
        self.word_idx = {}
        self.transMatrix = None    # TODO: how to declare?
        self.emitMatrix = None

        self.preprocess()

    def isline(self, line):
        if '.' not in line: return False
        if line == "": return False
        return True

    def get_posLines(self):

        unique_pos = set(['<s>','</s>'])

        for line in self.lines:
            pos_line = ['<s>']
            chunks = line.split('+')
            for chunk in chunks:
                _, pos = chunk.split('/')
                unique_pos.add(pos)
                pos_line.append(pos)
            pos_line.append('</s>')
            self.pos_lines.append(pos_line)

        # len needed to initialize transition matrix
        self.pos_len = len(unique_pos)
        for idx, pos in enumerate(unique_pos):
            self.pos_idx[pos] = idx

    def get_emitLines(self):

        unique_words= set()

        for line in self.lines:
            self.emit_lines.append(line.split('+'))

        for line in self.emit_lines:
            for chunk in line:
                word, _ = chunk.split('/')
                unique_words.add(word)

        self.word_len = len(unique_words)
        for ix, word in enumerate(unique_words):
            self.word_idx[word] = ix
        print(self.emit_lines)

    def preprocess(self):
        with open(self.path, "r", encoding="EUC-KR") as f:
            for line in f:
                line = line.strip()
                if self.isline(line):
                    line = line.split()[-1].strip()
                    self.lines.append(line)
    
    def compute_transition(self):
        self.get_posLines()
        self.transMatrix = [[0 for _ in range(self.pos_len)] for _ in range(self.pos_len)]

        # make bigram
        #pos_bigrams = []
        for pos_line in self.pos_lines:
            bigram = list(zip(pos_line[:-1], pos_line[1:]))
            self.pos_bigrams.append(bigram)

        # make bigram count matrix
        for pos_bigram in self.pos_bigrams:
            for pre, post in pos_bigram:
                self.transMatrix[self.pos_idx[pre]][self.pos_idx[post]] += 1

        # add 1 smoothing
        self.transMatrix = [[elem+1 for elem in row] for row in self.transMatrix]

        # normalize to get probablity
        for ix, row in enumerate(self.transMatrix):
            denom = sum(row)
            self.transMatrix[ix] = [elem/denom for elem in row]
       #print("self.transMatrix: final probablity\n", self.transMatrix)

    def compute_observation(self):
        self.get_emitLines()

        self.emitMatrix = [[0 for _ in range(self.word_len)] for _ in range(self.pos_len)]
        for line in self.emit_lines:
            for chunk in line:
                word, pos = chunk.split('/')
                self.emitMatrix[self.pos_idx[pos]][self.word_idx[word]] += 1

        # add 1 smoothing
        self.emitMatrix = [[elem + 1 for elem in row] for row in self.emitMatrix]

        # normalize to get probablity
        for ix, row in enumerate(self.emitMatrix):
            denom = sum(row)
            self.emitMatrix[ix] = [elem / denom for elem in row]
        #print("self.emitMatrix: final probablity\n", self.emitMatrix)

    def which_sent(self):

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
        max_idx = prob_lines.index(max(prob_lines))
        print(self.lines[max_idx]) 
       ### check if this implementation is correct

        pass
        # return "안녕/NNG+'하/NNG'+..."



