# -*- coding: utf-8 -*-

import pickle
from datetime import datetime
from csv import DictReader
from math import exp, log, sqrt
from util.ctr.dsp.pymmh3 import hash

class OnlineLearning(object):

    def __init__(self, alpha: float, adapt: float, fudge:float, signed = False, interaction = False):
        # learning rate for sgd optimization
        self.alpha = alpha
        # Use adagrad, sets it as power of adaptive factor. >1 will amplify adaptive measure and vice versa
        self.adapt = adapt
        # Fudge factor
        self.fudge = fudge
        # Use signed hash? Set to False for to reduce number of hash calls
        self.signed = signed
        self.interaction = interaction

        # number of weights use for learning
        self.D = 2 ** 24
        self.lambda1 = 0.
        self.lambda2 = 0.


    def logloss(self, p, y):
        """
        A. Bounded logloss
        :param p: our prediction
        :param y: real answer
        :return: logarithmic loss of p given y
        """
        # The bounds
        p = max(min(p, 1. - 10e-17), 10e-17)
        return -log(p) if y == 1. else -log(1. - p)


    def get_x(self, csv_row, D):
        """
        B. Apply hash trick of the original csv row
        for simplicity, we treat both integer and categorical features as categorical
        :param csv_row: a csv dictionary, ex: {'Lable': '1', 'I1': '357', 'I2': '', ...}
        :param D: the max index that we can hash to
        :return: a list of indices that its value is 1
        """
        fullind = []
        for key, value in csv_row.items():
            if value == None:
                value = ''
            s = key + '=' + value
            fullind.append(hash(s) % D)  # weakest hash ever ?? Not anymore :P

        if self.interaction == True:
            indlist2 = []
            for i in range(len(fullind)):
                for j in range(i + 1, len(fullind)):
                    indlist2.append(fullind[i] ^ fullind[j])  # Creating interactions using XOR
            fullind = fullind + indlist2

        x = {}
        x[0] = 1  # 0 is the index of the bias term
        for index in fullind:
            if (index not in x):
                # if(not x.has_key(index)):
                x[index] = 0
            if self.signed:
                x[index] += (1 if (hash(str(index)) % 2) == 1 else -1)  # Disable for speed
            else:
                x[index] += 1

        return x  # x contains indices of features that have a value as number of occurences


    def get_p(self, x, w):
        """
        C. Get probability estimation on x
        :param x: features
        :param w: weights
        :return: probability of p(y = 1 | x; w)
        """
        wTx = 0.
        for i, xi in x.items():
            # w[i] * x[i]
            wTx += w[i] * xi
        # bounded sigmoid
        return 1. / (1. + exp(-max(min(wTx, 50.), -50.)))


    def update_w(self, w, g, x, p, y):
        """
        D. Update given model
        :param w: weights
        :param g: a counter that counts the number of times we encounter a feature
                  this is used for adaptive learning rate
        :param x: feature
        :param p: prediction of our model
        :param y: answer
        :return: w: updated model, n: updated count
        """
        for i, xi in x.items():
            # alpha / (sqrt(g) + 1) is the adaptive learning rate heuristic
            # (p - y) * x[i] is the current gradient
            # note that in our case, if i in x then x[i] = 1
            delreg = (self.lambda1 * ((-1.) if w[i] < 0. else 1.) + self.lambda2 * w[i]) if i != 0 else 0.
            delta = (p - y) * xi + delreg
            if self.adapt > 0:
                g[i] += delta ** 2
            # Minimising log loss
            w[i] -= delta * self.alpha / (sqrt(g[i]) ** self.adapt)
        return w, g


class OnlineTraining(OnlineLearning):

    def __init__(self, from_alpha:float, to_alpha: float, adapt: float, fudge: float, signed = False, interaction = False):
        alpha = from_alpha if interaction else to_alpha
        super().__init__(alpha, adapt, fudge, signed, interaction)
        self.logbatch = 100000


    def train_data(self, train_file):
        """
        load train data and generate the weights
        :param train_file:
        :return: weights
        """
        # weights
        w = [0.] * self.D
        # sum of historical gradients
        g = [self.fudge] * self.D

        loss = 0.
        lossb = 0.
        # start training a logistic regression model using on pass sgd
        for t, row in enumerate(DictReader(open(train_file), delimiter=',', lineterminator='\n')):
            y = 1. if row['click'] == '1' else 0.

            # can't let the model peek the answer
            del row['click']

            # main training procedure
            # step 1, get the hashed features
            x = self.get_x(row, self.D)
            # step 2, get prediction
            p = self.get_p(x, w)

            # for progress validation, useless for learning our model
            lossx = self.logloss(p, y)
            loss += lossx
            lossb += lossx
            if t % self.logbatch == 0 and t > 1:
                print('%s\tencountered: %d\tcurrent whole logloss: %f\tcurrent batch logloss: %f' % (
                datetime.now(), t, loss / t, lossb / self.logbatch))
                lossb = 0.

            # step 3, update model with answer
            w, g = self.update_w(w, g, x, p, y)

        return w


    def _save_weight(self, file, w):
        """
        save weights to file
        :param file:
        :param w:
        :return:
        """
        with open(file, 'wb') as f:
            pickle.dump(w, f)


class OnlineService():
    # Here will be the instance stored.
    __instance = None

    @staticmethod
    def getInstance(w = None, learner = None):
        """ Static access method. """
        if OnlineService.__instance == None:
            OnlineService(w, learner)
        return OnlineService.__instance

    def __init__(self, w = None, learner = None):
        """ Virtually private constructor. """
        if OnlineService.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            # will be loaded later
            self.learner = learner
            self.w = w
            self.header = 'user_id,date_hour,exchange_id,app_id,adv_id,platform_id,device_type,ip,customer_cost,adv_size,group_id,campaign_id'.split(',')
            OnlineService.__instance = self


    def _row_to_dict(self, row) -> {}:
        result = {}

        data = row.split(',')
        for i in range(0, len(data)):
            result[self.header[i]] = data[i]

        return result


    def predict(self, data):
        row_list = data.split(';')
        row_size = len(row_list)
        result_list = [0] * row_size

        if self.w is not None and self.learner is not None:

            for i in range(0, row_size):
                value_map = self._row_to_dict(row_list[i])
                if len(value_map) == 12:
                    x = self.learner.get_x(value_map, self.learner.D)
                    result = self.learner.get_p(x, self.w)
                    result_list[i] = str(result)

        return ';'.join(result_list)

    def load_w(self, file):
        with open(file, 'rb') as train_model:
            self.w = pickle.load(train_model)


    def load_learner(self, alpha, adapt, fudge, signed = False, interaction = False):
        learner = OnlineLearning(alpha, adapt, fudge, signed, interaction)
        self.learner = learner
