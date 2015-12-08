import pickle
import math
from collections import defaultdict
from sentiment import helpers
from website.models import Comment
import json
import re


class NBClassifier(object):

    POSITIVE = Comment.POSITIVE
    NEGATIVE = Comment.NEGATIVE
    POLARITY = (POSITIVE, NEGATIVE)
    POS = ["PART", "SPRO", "ADV", "ADVPRO", "V", "INTJ", "COM",
           "NUM", "ANUM", "APRO", "CONJ", "A", "S", "PR", "NOT_RECOGNIZED"]

    def __init__(self, use_pos=False, stem=False):
        self.USE_POS = use_pos
        self.STEM = stem
        self.pos_vocab = {}
        self.pos_difference = {}
        if stem:
            self.stem_vocab = {}
        self.docs = self._dd()  # amount of docs for a class
        self.words = defaultdict(self._dd)  # all tokens
        self.words_amount = self._dd()  # total amount of words in each class
        self.vocab_length = self._dd()  # different words in each class
        self.p_class = self._dd()  # log of probability of a class

    def _dd(self):
        return {self.POSITIVE: 0, self.NEGATIVE: 0}

    @helpers.note_the_time(name="Tagging")
    def pos_tagging(self, data):
        docs = " ".join([doc['doc'].lower() for doc in data])
        tokens = helpers.tokenize(docs)
        dif_tokens = set(tokens)
        string_of_tokens = " ".join(dif_tokens).encode()
        output, errors = helpers.execute_mystem(string_of_tokens)
        mystem_data = json.loads(output.decode())
        for token in mystem_data:
            pos = helpers.get_pos(token, not_recognized="NOT_RECOGNIZED")
            stem = token['analysis'][0]['lex'] if token['analysis'] else None
            self.pos_vocab[token['text']] = {"POS": pos, "stem": stem}

    @helpers.note_the_time(name="Training")
    def train(self, data, positive_label, occurrence=0, delete_pos=None):
        # TODO: fix stemming
        # if self.STEM:
        #     docs = " ".join([doc['doc'].lower() for doc in data])
        #     tokens = helpers.tokenize(docs)
        #     dif_tokens = set(tokens)
        #     string_of_tokens = " ".join(dif_tokens).encode()
        #     output, errors = helpers.execute_mystem(string_of_tokens)
        #     mystem_data = json.loads(output.decode())
        #     for token in mystem_data:
        #         pos = re.findall(r'[A-Z]+', token['analysis'][0]['gr'])[0] if token['analysis'] \
        #             else "NOT RECOGNIZED"
        #         stem = token['analysis'][0]['lex'] if token['analysis'] else None
        #         self.stem_vocab[token['text']] = {"POS": pos, "stem": stem}

        for doc in data:
            cl = self.POSITIVE if doc['polarity'] == positive_label else self.NEGATIVE
            self.docs[cl] += 1
            tokens = helpers.tokenize(doc['doc'].lower())
            for token in tokens:
                self.words[token][cl] += 1

        if delete_pos:
            for token in self.pos_vocab:
                pos = self.pos_vocab[token]["POS"]
                if pos == delete_pos:
                    self.words.pop(token, None)

        if occurrence:
            for token in self.words:
                for cl in self.POLARITY:
                    if self.words[token][cl] <= occurrence:
                        self.words[token][cl] = 0

        # TODO: delete this using part of speech and make new
        # if self.USE_POS:
        #     string_of_tokens = " ".join(self.words.keys()).encode()
        #     output, errors = helpers.execute_mystem(string_of_tokens)
        #     mystem_data = json.loads(output.decode())
        #     pos_count = defaultdict(lambda: {self.POSITIVE: 0, self.NEGATIVE: 0})
        #     for token in mystem_data:
        #         pos = re.findall(r'[A-Z]+', token['analysis'][0]['gr'])[0] if token['analysis'] \
        #             else None
        #         if not pos:
        #             continue
        #         self.pos_vocab[token['text']] = pos
        #         for cl in self.CLS:
        #             pos_count[pos][cl] += self.words[token['text']][cl]
        #     all_positive = sum([i[self.POSITIVE] for i in pos_count.values()])
        #     all_negative = sum([i[self.NEGATIVE] for i in pos_count.values()])
        #     for pos, count in pos_count.items():
        #         rel_positive = count[self.POSITIVE]/all_positive
        #         rel_negative = count[self.NEGATIVE]/all_negative
        #         difference = rel_positive - rel_negative
        #         self.pos_difference[pos] = difference

        for cl in self.POLARITY:
            self.p_class[cl] = math.log(
                self.docs[cl]/len(data) if self.docs[cl] and data else 1)
            self.vocab_length[cl] = sum(
                [1 if token[cl] else 0 for token in self.words.values()])
            self.words_amount[cl] = sum(
                [token[cl] for token in self.words.values()])

    @helpers.note_the_time(name="Prediction")
    def predict(self, data):
        labels = []
        for doc in data:
            score = self.p_class.copy()
            for cl in self.POLARITY:
                tokens = helpers.tokenize(doc['text'].lower())
                for token in tokens:
                    count = self.words[token][cl]
                    probability = (count+1) / (self.words_amount[cl]+self.vocab_length[cl]) \
                        if self.words_amount[cl] else 1
                    if self.USE_POS:
                        pass
                    score[cl] += math.log(probability)
            polarity = self.POSITIVE if score[self.POSITIVE] > score[self.NEGATIVE] \
                else self.NEGATIVE
            labels.append({'id': doc['id'], 'polarity': polarity})
        return labels

    def evaluate(self, labels, true_labels, positive_label):
        cs = 0    # correct selected, true positive
        cns = 0   # correct not selected, false negative
        ncs = 0   # not correct selected, false positive
        ncns = 0  # not correct not selected, true negative
        false_negative = []
        false_positive = []

        for i in range(len(true_labels)):
            if true_labels[i]['polarity'] == positive_label:
                if labels[i] == self.POSITIVE:
                    cs += 1
                else:
                    cns += 1
                    false_negative.append(true_labels[i]['doc'])
            else:
                if labels[i] == self.NEGATIVE:
                    ncns += 1
                else:
                    ncs += 1
                    false_positive.append(true_labels[i]['doc'])

        # accuracy
        acc = (cs + ncns)/(cs + ncs + ncns + cns) if \
            cs+ncs+ncns+cns else 0
        # recall (sensitivity or true positive rate)
        rec = cs/(cs + cns) if cs+cns else 0
        # precision or positive prediction value
        ppv = cs/(cs + ncs) if cs+ncs else 0
        # negative prediction value
        npv = ncns/(ncns + cns) if ncns+cns else 0
        # F1 measure
        f1 = 2*ppv*rec / (ppv+rec) if ppv+rec else 0
        return {
            "all": (cs, ncs, ncns, cns),
            "accuracy": acc,
            "recall": rec,
            "ppv": ppv,
            "npv": npv,
            "F1": f1
        }, false_negative, false_positive

    def save(self, path):
        f = open(path, 'wb')
        pickle.dump(self, f)
        f.close()

    @staticmethod
    def load(path):
        f = open(path, 'rb')
        obj = pickle.load(f)
        f.close()
        return obj