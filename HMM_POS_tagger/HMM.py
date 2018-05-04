import math

class HMM():
    def __init__(self, path):
        self.MAX = 32
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
        unique_pos = set(['<s>', '</s>'])
        pos_lines = []
        for line in lines:
            pos_line = ['<s>']
            for eojeol in line:
                chunks = eojeol.split('+')
                for chunk in chunks:
                    # TODO : if-else exceptions
                    if chunk == "//SP":                 # //SP
                        pos = 'SP'
                    elif chunk == "": continue          # ++/SW
                    else:
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
        unique_words = set()
        emit_lines = []
        for line in lines:
            emit_line = []
            for eojeol in line:
                emit_line.extend(eojeol.split("+"))
            emit_lines.append(emit_line)

        for line in emit_lines:
            for chunk in line:
                # TODO: if-else exceptions
                if chunk == "//SP":            # //SP
                    word = '/'
                elif chunk == "": continue     # ++/SW
                elif chunk == "/SW":           # ++/SW
                    word = '+'
                else:
                    word, _ = chunk.split('/')
                unique_words.add(word)

        self.word_len = len(unique_words)
        for ix, word in enumerate(unique_words):
            self.word_idx[word] = ix
        # FIXME: unk?!
        self.word_idx['UNK'] = len(self.word_idx)
        return emit_lines

    def preprocess(self):
        with open(self.path, "r", encoding="CP949") as f:
            sentence = []
            for line in f:
                if line=="\n":
                    self.lines.append(sentence)
                    sentence = []
                    continue
                line = line.split()[-1].strip()
                sentence.append(line)

    def make_bigram(self, pos_lines):
        pos_bigrams = []
        for pos_line in pos_lines:
            bigram = list(zip(pos_line[:-1], pos_line[1:]))
            pos_bigrams.append(bigram)
        return pos_bigrams

    def compute_transition(self):
        pos_lines = self.get_posLines(self.lines)
        self.transMatrix = [[0 for _ in range(self.pos_len)] for _ in range(self.pos_len)]
        pos_bigrams = self.make_bigram(pos_lines)

        # make bigram count matrix
        for pos_bigram in pos_bigrams:
            for pre, post in pos_bigram:
                self.transMatrix[self.pos_idx[pre]][self.pos_idx[post]] += 1

        # add 1 smoothing
        self.transMatrix = [[elem + 1 for elem in row] for row in self.transMatrix]

        # normalize to get probablity
        for ix, row in enumerate(self.transMatrix):
            denom = sum(row)
            self.transMatrix[ix] = [elem / denom for elem in row]

    def compute_observation(self):
        emit_lines = self.get_emitLines(self.lines)
        self.emitMatrix = [[0 for _ in range(self.word_len)] for _ in range(self.pos_len)]

        for line in emit_lines:
            for chunk in line:
                # TODO: if-else exceptions?
                if chunk == "//SP":                  # //SP
                    word, pos = ('/', 'SP')
                elif chunk == "": continue           # ++/SW
                elif chunk == "/SW":                 # ++/SW
                    word, pos = ('+', 'SW')
                else:
                    word, pos = chunk.split('/')
                self.emitMatrix[self.pos_idx[pos]][self.word_idx[word]] += 1

        # add 1 smoothing
        self.emitMatrix = [[elem + 1 for elem in row] for row in self.emitMatrix]

        # normalize to get probablity
        for ix, row in enumerate(self.emitMatrix):
            denom = sum(row)
            self.emitMatrix[ix] = [elem / denom for elem in row]

    def train(self):
        print("Training HMM from \"%s\"" % self.path)
        self.compute_transition()
        self.compute_observation()
        print("Training finished!")

    # cell = '먹/VV+었/EP+니/EF+?/SF'
    def get_prob(self, cell):
        chunks = cell.split('+')
        posline = [chunk.split('/')[-1] for chunk in chunks]
        emitline = [chunk.split('/') for chunk in chunks]

        prob = 0
        # trainsition probability
        for pre, post in zip(posline[:-1], posline[1:]):
            prob += math.log(self.transMatrix[self.pos_idx[pre]][self.pos_idx[post]])
        # emission probability
        for (morph, pos) in emitline:
            try:
                prob += math.log(self.emitMatrix[self.pos_idx[pos]][self.word_idx[morph]])
            # FIXME: unknown word
            except:
                return -3000000   # small number
        return prob

    # cell = '먹/VV+었/EP+니/EF+?/SF'
    def get_start(self, cell):
        return self.pos_idx[cell.split('+')[0].split('/')[-1]]    # VV의 idx

    # cell = '먹/VV+었/EP+니/EF+?/SF'
    def get_end(self, cell):
        return self.pos_idx[cell.split('+')[-1].split('/')[-1]]    # SF의 idx

    def predict(self, sent_eojeol, sent_pos):
        f = open("output.txt", "w", encoding="utf-8")
        for n_sent in range(len(sent_eojeol)):
            n_eojeol = len(sent_eojeol[n_sent])
            lattice = [[None for _ in range(n_eojeol)] for _ in range(self.MAX)]
            viterbi = [[None for _ in range(n_eojeol)] for _ in range(self.MAX)]
            backtrace = [[None for _ in range(n_eojeol+1)] for _ in range(self.MAX)]

            # fill up lattice
            for col in range(n_eojeol):
                n_pos = len(sent_pos[n_sent][col])
                for row in range(n_pos):
                    lattice[row][col] = (self.get_prob(sent_pos[n_sent][col][row]),
                                         self.get_start(sent_pos[n_sent][col][row]),
                                         self.get_end(sent_pos[n_sent][col][row]))

            # fill up viterbi table
            for col in range(n_eojeol):
                n_pos = len(sent_pos[n_sent][col])
                for row in range(n_pos):
                    # init
                    if col is 0:
                        viterbi[row][col] = lattice[row][col][0]\
                                            + math.log(self.transMatrix[self.pos_idx['<s>']][lattice[row][col][1]])
                        backtrace[row][col] = -1 # finish symbol
                        continue
                    # recursion
                    else:
                        candidates = [viterbi[i][col-1]
                              + math.log(self.transMatrix[lattice[i][col-1][2]][lattice[row][col][1]])
                              for i in range(len(sent_pos[n_sent][col-1]))]
                        viterbi[row][col] = max(candidates)
                        backtrace[row][col]= candidates.index(max(candidates))
            # termination
            last_col = n_eojeol-1
            #candidates = [viterbi[i][last_col] for i in range(len(sent_pos[n_sent][last_col]))]
            candidates = [viterbi[i][last_col]
                          + math.log(self.transMatrix[lattice[i][last_col][2]][self.pos_idx['</s>']])
                          for i in range(len(sent_pos[n_sent][last_col]))]
            backtrace[0][last_col+1] = candidates.index(max(candidates))

            # backtrace
            answer_idx = []
            back_idx = 0
            for col in reversed(range(n_eojeol)):
                back_idx = backtrace[back_idx][col+1]
                answer_idx.insert(0, back_idx)
            print("\n===answers===")
            for eojeol_idx, pos_idx in zip(range(n_eojeol), answer_idx):
                token = sent_pos[n_sent][eojeol_idx][pos_idx]
                print(token)
                f.write(token+" ")
            f.write("\n")
        f.close()

    # def test(self):
    #     prob1 = self.get_prob("안녕/NNG+하/NNG+세/VV+요/EC")
    #     #prob1 += math.log(self.transMatrix[self.pos_idx['<s>']][self.pos_idx['NNG']])
    #     prob1_with_end = prob1 + math.log(self.transMatrix[self.pos_idx['EC']][self.pos_idx['</s>']])
    #     prob2 = self.get_prob("안녕/NNG+하/XSV+세/EC+요/JX")
    #     #prob2 += math.log(self.transMatrix[self.pos_idx['<s>']][self.pos_idx['NNG']])
    #     prob2_with_end = prob2 + math.log(self.transMatrix[self.pos_idx['JX']][self.pos_idx['</s>']])
    #     print("안녕/NNG+하/NNG+세/VV+요/EC without </s>\n", prob1)
    #     print("안녕/NNG+하/NNG+세/VV+요/EC with </s>\n", prob1_with_end)
    #     print("안녕/NNG+하/XSV+세/EC+요/JX without </s>\n", prob2)
    #     print("안녕/NNG+하/XSV+세/EC+요/JX with </s>\n", prob2_with_end)
