import numpy as np
import os
import tensorflow as tf

# shared global variables to be imported from model also
UNK = "$UNK$"
NUM = "$NUM$"
NONE = "O"

def minibatches(data, minibatch_size):
    """
    Args:
        data: generator of (sentence, tags) tuples
        minibatch_size: (int)

    Yields:
        list of tuples

    """
    x_batch, y_batch = [], []
    for (x, y) in data:
        if len(x_batch) == minibatch_size:
            yield x_batch, y_batch
            x_batch, y_batch = [], []

        if type(x[0]) == tuple:
            x = zip(*x)
        x_batch += [x]
        y_batch += [y]

    if len(x_batch) != 0:
        yield x_batch, y_batch

def _pad_sequences(sequences, pad_tok, max_length):
    """
    Args:
        sequences: a generator of list or tuple
        pad_tok: the char to pad with

    Returns:
        a list of list where each sublist has same length
    """
    sequence_padded, sequence_length = [], []

    for seq in sequences:
        seq = list(seq)
        seq_ = seq[:max_length] + [pad_tok]*max(max_length - len(seq), 0)
        sequence_padded +=  [seq_]
        sequence_length += [min(len(seq), max_length)]

    return sequence_padded, sequence_length

def pad_sequences(sequences, pad_tok, nlevels=1):
    """
    Args:
        sequences: a generator of list or tuple
        pad_tok: the char to pad with
        nlevels: "depth" of padding, for the case where we have characters ids

    Returns:
        a list of list where each sublist has same length

    """
    if nlevels == 1:
        max_length = max(map(lambda x : len(x), sequences))
        sequence_padded, sequence_length = _pad_sequences(sequences,
                                            pad_tok, max_length)

    elif nlevels == 2:
        max_length_word = max([max(map(lambda x: len(x), seq))
                               for seq in sequences])
        sequence_padded, sequence_length = [], []
        for seq in sequences:
            # all words are same length now
            sp, sl = _pad_sequences(seq, pad_tok, max_length_word)
            sequence_padded += [sp]
            sequence_length += [sl]

        max_length_sentence = max(map(lambda x : len(x), sequences))
        sequence_padded, _ = _pad_sequences(sequence_padded,
                [pad_tok]*max_length_word, max_length_sentence)
        sequence_length, _ = _pad_sequences(sequence_length, 0,
                max_length_sentence)

    return sequence_padded, sequence_length

def get_chunks(seq, tags):
    """Given a sequence of tags, group entities and their position

    Args:
        seq: [4, 4, 0, 0, ...] sequence of labels
        tags: dict["O"] = 4

    Returns:
        list of (chunk_type, chunk_start, chunk_end)

    Example:
        seq = [4, 5, 0, 3]
        tags = {"B-PER": 4, "I-PER": 5, "B-LOC": 3}
        result = [("PER", 0, 2), ("LOC", 3, 4)]

    """
    default = tags[NONE]
    idx_to_tag = {idx: tag for tag, idx in tags.items()}
    chunks = []
    chunk_type, chunk_start = None, None
    for i, tok in enumerate(seq):
        # End of a chunk 1
        if tok == default and chunk_type is not None:
            # Add a chunk.
            chunk = (chunk_type, chunk_start, i)
            chunks.append(chunk)
            chunk_type, chunk_start = None, None

        # End of a chunk + start of a chunk!
        elif tok != default:

            tag_name = idx_to_tag[tok]
            tok_chunk_class = tag_name.split('-')[0]
            tok_chunk_type = tag_name.split('-')[-1]

            if chunk_type is None:
                chunk_type, chunk_start = tok_chunk_type, i
            elif tok_chunk_type != chunk_type or tok_chunk_class == "B":
                chunk = (chunk_type, chunk_start, i)
                chunks.append(chunk)
                chunk_type, chunk_start = tok_chunk_type, i
        else:
            pass

    # end condition
    if chunk_type is not None:
        chunk = (chunk_type, chunk_start, len(seq))
        chunks.append(chunk)

    return chunks


class NERmodel(object):
    """Generic class for general methods that are not specific to NER"""

    def __init__(self, config):
        """Defines self.config and self.logger

        Args:
            config: (Config instance) class with hyper parameters,
                vocab and embeddings

        """
        self.config = config
        self.sess   = None
        self.saver  = None
        # why?
        self.idx_to_tag = {idx: tag for tag, idx in
                           self.config.vocab_tags.items()}

    def build(self):
        # QUESTION: sequence_lengths를 쓰겠다는 건, padding을 안 하겠다는 거 아닌가?
        self.sequence_lengths = tf.placeholder(dtype=tf.int32, shape=[None], name="sequence_lengths")
        # batch_size
        self.labels = tf.placeholder(dtype=tf.int32, shape=[None, None], name="labels")
        # batch_size x max_len
        self.dropout = tf.placeholder(dtype=tf.float32, shape=[], name="dropout")
        # scalar
        self.lr = tf.placeholder(dtype=tf.float32, shape=[], name="lr")
        # scalar
        self.word_ids = tf.placeholder(dtype=tf.int32, shape=[None,None], name="word_ids")
        # batch_size x max_len

        # QUESTION: variable_scope
        with tf.variable_scope("words"):
            if self.config.use_pretrained is False:
                print("Randomly initializing word vectors")
                _word_embeddings = tf.get_variable(
                    name="_word_embeddings",
                    dtype=tf.float32,
                    shape=[self.config.nwords, self.config.dim_word])

            else:
                print("Using pre-trained word vectors :" + self.config.filename_embedding)
                _word_embeddings = tf.Variable(
                    self.config.embeddings,    # numpy array    
                    name="_word_embeddings",
                    dtype=tf.float32)

            # QUESTION: tf.nn? tf.contrib?
            word_embeddings = tf.nn.embedding_lookup(_word_embeddings,
                                                     self.word_ids, name="word_embedding")
        self.word_embeddings = word_embeddings
        # (batch_size, max_len, 50)

        # NOTE: alias tf.nn.rnn_cell.LSTMCell
        cell_fw = tf.contrib.rnn.LSTMCell(self.config.hidden_size_lstm)
        cell_bw = tf.contrib.rnn.LSTMCell(self.config.hidden_size_lstm)
        # returns (outputs, output_states)
        # 'outputs' is a tensor of shape [batch_size, max_time, cell_state_size]
        # QUESTION: dynamic vs static?
        # QUESTION: padding하는 건가? feed_dict 주의 깊게 보자
        (output_fw, output_bw), _ = tf.nn.bidirectional_dynamic_rnn(
            cell_fw, cell_bw, self.word_embeddings, sequence_length=self.sequence_lengths, dtype=tf.float32)
        # 같은 batch의 같은 time_step일 때 concat!
        output = tf.concat([output_fw, output_bw], axis=-1)
        # 이건 옵션 또 뭘까~
        output = tf.nn.dropout(output, self.dropout)

        # time step
        nsteps = tf.shape(output)[1]    

        # QUESTION: 엥?? 다 뭉게버림??
        output = tf.reshape(output, [-1, 2*self.config.hidden_size_lstm])

        # output의 shape x self.config.ntag
        W = tf.get_variable(name="W", dtype=tf.float32,
            shape=[2*self.config.hidden_size_lstm, self.config.ntags])
        # self.config.ntags
        b = tf.get_variable(name="b", dtype=tf.float32,
            shape=[self.config.ntags], initializer=tf.zeros_initializer())
        pred = tf.matmul(output, W) + b

        # QUESTION: shape 왜 이따구냐ㅠ
        self.logits = tf.reshape(pred, [-1, nsteps, self.config.ntags])

        losses = tf.nn.sparse_softmax_cross_entropy_with_logits(
            logits=self.logits, labels=self.labels)
        self.loss = tf.reduce_mean(losses)
        self.labels_pred = tf.cast(tf.argmax(self.logits, axis=-1), tf.int32)

        optimizer = tf.train.AdamOptimizer(self.lr)
        self.train_op = optimizer.minimize(self.loss)

        self.sess = tf.Session()
        self.sess.run(tf.global_variables_initializer())
        self.saver = tf.train.Saver()


    def train(self, train, dev):
        """Performs training with early stopping and lr exponential decay

        Args:
            train: dataset that yields tuple of (sentences, tags)
            dev: dataset

        """
        best_score = 0
        nepoch_no_imprv = 0 # for early stopping

        for epoch in range(self.config.nepochs):
            print("Epoch {:} out of {:}".format(epoch + 1, self.config.nepochs))

            #score = self.run_epoch(train, dev, epoch)

            #############3
            batch_size = self.config.batch_size
            #nbatches = (len(train) + batch_size - 1)

            # iterate over dataset
            for i, (words, labels) in enumerate(minibatches(train, batch_size)):
                fd, _ = self.get_feed_dict(words, labels, self.config.lr,
                                           self.config.dropout)

                _, train_loss = self.sess.run(
                    [self.train_op, self.loss], feed_dict=fd)

                # print(i + 1, [("train loss", train_loss)])

            metrics = self.run_evaluate(dev)
            print("acc : " + str('%.2f' % metrics['acc']) + " - " + "f1 : " + str('%.2f' % metrics['f1']))

            score = metrics["f1"]
            ########## ju_edit
            self.config.lr *= self.config.lr_decay # decay learning rate

            # early stopping and saving best parameters
            if score >= best_score:
                nepoch_no_imprv = 0
                if not os.path.exists(self.config.dir_model):
                    os.makedirs(self.config.dir_model)
                self.saver.save(self.sess, self.config.dir_model)
                best_score = score
                print ("new best score")
            else:
                nepoch_no_imprv += 1
                if nepoch_no_imprv >= self.config.nepoch_no_imprv:
                    print ("- early stopping {} epochs without ""improvement".format(nepoch_no_imprv))
                    break

    def restore_session(self, dir_model):
        """Reload weights into session

        Args:
            sess: tf.Session()
            dir_model: dir with weights

        """
        print("Reloading the latest trained model...")
        self.saver.restore(self.sess, dir_model)

    def run_evaluate(self, test):

        """Evaluates performance on test set

        Args:
            test: dataset that yields tuple of (sentences, tags)

        Returns:
            metrics: (dict) metrics["acc"] = 98.4, ...

        """
        accs = []
        correct_preds, total_correct, total_preds = 0., 0., 0.
        for words, labels in minibatches(test, self.config.batch_size):
            labels_pred, sequence_lengths = self.predict_batch(words)

            for lab, lab_pred, length in zip(labels, labels_pred,
                                             sequence_lengths):
                lab = lab[:length]
                lab_pred = lab_pred[:length]
                accs += [a == b for (a, b) in zip(lab, lab_pred)]

                lab_chunks = set(get_chunks(lab, self.config.vocab_tags))
                lab_pred_chunks = set(get_chunks(lab_pred,
                                                 self.config.vocab_tags))

                correct_preds += len(lab_chunks & lab_pred_chunks)
                total_preds += len(lab_pred_chunks)
                total_correct += len(lab_chunks)

        p = correct_preds / total_preds if correct_preds > 0 else 0
        r = correct_preds / total_correct if correct_preds > 0 else 0
        f1 = 2 * p * r / (p + r) if correct_preds > 0 else 0
        acc = np.mean(accs)

        return {"acc": 100 * acc, "f1": 100 * f1}

    def get_feed_dict(self, words, labels=None, lr=None, dropout=None):
        """Given some data, pad it and build a feed dictionary

        Args:
            words: list of sentences. A sentence is a list of ids of a list of
                words. A word is a list of ids
            labels: list of ids
            lr: (float) learning rate
            dropout: (float) keep prob

        Returns:
            dict {placeholder: value}

        """
        # perform padding of the given data

        word_ids, sequence_lengths = pad_sequences(words, 0)

        # build feed dictionary
        feed = {
            self.word_ids: word_ids,
            self.sequence_lengths: sequence_lengths
        }

        if labels is not None:
            labels, _ = pad_sequences(labels, 0)
            feed[self.labels] = labels

        if lr is not None:
            feed[self.lr] = lr

        if dropout is not None:
            feed[self.dropout] = dropout

        return feed, sequence_lengths

    def predict_batch(self, words):
        """
        Args:
            words: list of sentences

        Returns:
            labels_pred: list of labels for each sentence
            sequence_length

        """
        fd, sequence_lengths = self.get_feed_dict(words, dropout=1.0)

        labels_pred = self.sess.run(self.labels_pred, feed_dict=fd)

        return labels_pred, sequence_lengths

    def predict(self, words_raw):
        """Returns list of tags

        Args:
            words_raw: list of words (string), just one sentence (no batch)

        Returns:
            preds: list of tags (string), one for each word in the sentence

        """
        words = [self.config.processing_word(w) for w in words_raw]
        if type(words[0]) == tuple:
            words = zip(*words)
        pred_ids, _ = self.predict_batch([words])
        preds = [self.idx_to_tag[idx] for idx in list(pred_ids[0])]

        return preds



