from HMM import HMM

if __name__=="__main__":

    path = './HMM_SMASH/result.txt'
    hmm = HMM(path)
    hmm.compute_transition()
    hmm.compute_observation()
    hmm.which_sent()
