import sqlite3
from . import classifier
from django.conf import settings
import os.path


def _get_data():
    path = os.path.join(settings.BASE_DIR, 'sentiment', 'twitter.db')
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute('select polarity, doc from corpora where polarity="neg"')
    data_negative = cur.fetchall()
    cur.execute('select polarity, doc from corpora where polarity="pos"')
    data_positive = cur.fetchall()
    con.close()
    return data_negative, data_positive


def _get_folder(p_data, n_data, folders, cur_folder):
    p_size = len(p_data)//folders
    n_size = len(n_data)//folders
    p_start = cur_folder * p_size
    n_start = cur_folder * n_size
    p_end = p_start + p_size
    n_end = n_start + n_size

    train_set = p_data[:p_start] + p_data[p_end:] + n_data[:n_start] + n_data[n_end:]
    test_set = p_data[p_start:p_end] + n_data[n_start:n_end]
    return train_set, test_set


def main():
    dn, dp = _get_data()
    nb = classifier.NBClassifier()
    nb.train(dn+dp, "pos")
    path = os.path.join(settings.BASE_DIR, 'sentiment', 'NaiveBayes')
    nb.save(path)


if __name__ == "__main__":
    main()