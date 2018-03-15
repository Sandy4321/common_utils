import os
import logging

import numpy as np
import torch
from torch.autograd import Variable
from torch.nn import Parameter


def cuda(obj):
    if torch.cuda.is_available():
        obj = obj.cuda()

    return obj


def variable(obj, volatile=False):
    if isinstance(obj, (list, tuple)):
        return [variable(o, volatile=volatile) for o in obj]

    if isinstance(obj, np.ndarray):
        obj = torch.from_numpy(obj)

    obj = cuda(obj)
    obj = Variable(obj, volatile=volatile)
    return obj


def get_trainable_parameters(parameters):
    parameters = list(parameters)
    nb_params_before = sum(p.nelement() for p in parameters)

    parameters = [p for p in parameters if p.requires_grad]
    nb_params_after = sum(p.nelement() for p in parameters)

    logging.info(f'Parameters: {nb_params_before} -> {nb_params_after}')
    return parameters


def set_variable_repr():
    Variable.__repr__ = lambda x: f'Variable {tuple(x.size())}'
    Parameter.__repr__ = lambda x: f'Parameter {tuple(x.size())}'


def get_sequences_lengths(sequences, masking=0, dim=1):
    if len(sequences.size()) > 2:
        sequences = sequences.sum(dim=2)

    masks = torch.ne(sequences, masking)

    lengths = masks.sum(dim=dim)

    return lengths


def argmax(inputs, dim=-1):
    values, indices = inputs.max(dim=dim)
    return indices


def restore_weights(model, filename):
    map_location = None

    # load trained on GPU models to CPU
    if not torch.cuda.is_available():
        map_location = lambda storage, loc: storage

    state_dict = torch.load(str(filename), map_location=map_location)

    if isinstance(model, torch.nn.DataParallel):
        model = model.module

    model.load_state_dict(state_dict)

    logging.info(f'Model restored: {filename}')


def save_weights(model, filename):
    if isinstance(model, torch.nn.DataParallel):
        model = model.module

    torch.save(model.state_dict(), str(filename))

    logging.info(f'Model saved: {filename}')