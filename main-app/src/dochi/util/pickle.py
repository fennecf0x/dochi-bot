import os
from os import path, makedirs
import errno
import pickle


def save_pickle(obj, p, name):
    filename = path.join(os.environ["CACHE_PATH"], p, name + '.pkl')
    if not path.exists(path.dirname(filename)):
        try:
            makedirs(path.dirname(filename))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    with open(filename, 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_pickle(p, name):
    with open(path.join(os.environ["CACHE_PATH"], p, name + '.pkl'), 'rb') as f:
        return pickle.load(f)