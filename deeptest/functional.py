# AUTOGENERATED! DO NOT EDIT! File to edit: 01_activation.ipynb (unless otherwise specified).

__all__ = ['query', 'WolframTester']

# Cell
import wolframalpha
from fastcore.test import *
from torch import nn
import torch
import torch.nn.functional as F
import re
import numpy as np
import pickle

# Cell
def query(expr, api_key):
    client = wolframalpha.Client(api_key)
    res = client.query(expr)
    vals = list()
    for pod in res.pods:
        if pod['@title'] == 'Result':
            val = float(pod['subpod']['plaintext'][:6])
            vals.append(val)
    return np.array(val)

# Cell
class WolframTester():

    def __init__(self, api_key, libdl):
        self.key = api_key
        self.libdl = libdl
        self.cache = None

    def test(self, fn, fn_expr, xs, shape):

        if (self.cache is not None):
            self.test_cache(fn, fn_expr, xs, shape)
            return

        if (self.libdl == 'torch'):
            ys = fn(xs).cpu().numpy()
            test_eq(ys.shape, shape)
            _xs = xs.cpu().detach().numpy().flatten()

        reals = list()

        for x in _xs:
            expr = re.sub('x', str(x), fn_expr)
            res = query(expr, self.key)
            reals.append(res)

        reals = np.array(reals).reshape(shape)
        np.testing.assert_allclose(ys, reals, rtol=1e-2, atol=1e-5)

        self.cache = {fn_expr : (xs, reals)}
        self.save_cache(fn.__name__)


    def test_cache(self, fn, fn_expr, xs, shape):
        self.load_cache(fn.__name__)
        xs, reals = self.cache[fn_expr]

        if (self.libdl == 'torch'):
            ys = fn(xs).cpu().numpy()
            test_eq(ys.shape, shape)
            xs = xs.cpu().detach().numpy().flatten()

        np.testing.assert_allclose(ys, reals, rtol=1e-2, atol=1e-5)


    def save_cache(self, name):
        with open(f'{name}.pkl', 'wb') as f:
            pickle.dump(self.cache, f, pickle.HIGHEST_PROTOCOL)
            print("Stored Cache")

    def load_cache(self, name):
        with open(f'{name}.pkl', 'rb') as f:
            self.cache = pickle.load(f)
            print("Loaded Cache")