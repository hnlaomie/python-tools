# -*- coding: utf-8 -*-

from sklearn.metrics import roc_curve, auc, roc_auc_score
import matplotlib.pyplot as plt

def roc_sample():
    test = [0, 1, 0, 1, 0, 1, 0]
    pred = [0.03, 0.05, 0.02, 0.06, 0.07, 0.05, 0.1]

    fpr = dict()
    tpr = dict()
    roc_auc = dict()
    for i in range(2):
        fpr[i], tpr[i], _ = roc_curve(test, pred)
        roc_auc[i] = auc(fpr[i], tpr[i])

    print(roc_auc_score(test, pred))
    plt.figure()
    plt.plot(fpr[1], tpr[1])
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver operating characteristic')
    plt.show()


if __name__ == '__main__':
    roc_sample()