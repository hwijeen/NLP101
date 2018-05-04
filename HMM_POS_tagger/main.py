from HMM import HMM

def isline(line):
    if line == "": return False
    if line == "\n": return False
    if "." not in line: return False
    return True

def get_sentences(path):
    sent_eojeol = []
    sent_pos = []
    with open(path, 'r', encoding='EUC-KR') as f:
        queries = f.read().replace('\n\n','\n').split('\n\n')[:-1]
        if len(queries) == 0:    # input with 1 query
            queries = f.read().replace('\n\n', '\n').split('\n\n')
        for sent_ix, query in enumerate(queries):
            no_pos_ix = []
            eojeol = []
            pos = []

            # make sent_eojeol = [['안녕하세요'], ['밥', '먹었니?']]
            query_lines = query.split('\n')
            for ix, line in enumerate(query_lines):
                if line[0] is not " " and not line[0].isdigit():
                    eojeol.append(line)
                    no_pos_ix.append(ix)
                else:    # for processing pos later
                    query_lines[ix] = line.split(".")[-1].strip()
            no_pos_ix.append(ix+1)
            sent_eojeol.append(eojeol)

            # make sent_pos = [[['안녕/NNG+하/NNG+세/NNB+요/EC', ...], [['밥/NNG', '밥/NNP'], ['먹/VV+었/EP+니/EF+?/SF', ...]]]
            for (i, j) in zip(no_pos_ix[:-1], no_pos_ix[1:]):
                pos.append(query_lines[i+1:j])
            sent_pos.append(pos)
    return sent_eojeol, sent_pos

if __name__=="__main__":

    train_path ='./HMM_SMASH/train.txt'
    test_path = './HMM_SMASH/result.txt'

    sent_eojeol, sent_pos = get_sentences(test_path)

    hmm = HMM(train_path)
    hmm.train()
    hmm.predict(sent_eojeol, sent_pos)
    #hmm.test()