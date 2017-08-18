#!/usr/bin/pypy

import pickle
from util.ctr.dsp.dsp_predict import OnlineTraining

def do_train():
    # 训练参数
    from_alpha = .01
    to_alpha = .1
    adapt = .4
    fudge = .08

    train = OnlineTraining(from_alpha, to_alpha, adapt, fudge)
    w = train.train_data('data/dsp_train_28.csv')
    with open('data/dsp_model.csv', 'wb') as f:
        pickle.dump(w, f)


if __name__ == '__main__':
    do_train()

