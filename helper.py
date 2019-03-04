#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pickle
import torch
from torchvision import datasets
from collections import Counter


def batch_data(words, sequence_length, batch_size):
    """
    Batch the neural network data using DataLoader
    Args:
      words (list): int-encoded words from the tv scripts
      sequence_length (int): sequence length of each batch
      batch_size (int): size of each batch; the number of sequences in a batch
    Returns:
      DataLoader: dataloader with batched data
    """
    n_batches = len(words)//batch_size
    # only full batches
    words = words[:n_batches*batch_size]
    target_idx = len(words) - sequence_length
    x, y = [], []
    for idx in range(0, target_idx):
        end = idx+sequence_length
        batch_x = words[idx:end]
        x.append(batch_x)
        batch_y = words[end]
        y.append(batch_y)

    dataset = torch.utils.data.TensorDataset(torch.tensor(x), torch.tensor(y))
    dataloader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)
    # return a dataloader
    return dataloader


def save_model(filename, model):
    """ 
    Save the model.
    Args:
        filename (str): filname for the model
        model: model to be saved
    """
    save_filename = os.path.splitext(os.path.basename(filename))[0] + '.pt'
    torch.save(model, save_filename)


def load_model(filename):
    save_filename = os.path.splitext(os.path.basename(filename))[0] + '.pt'
    return torch.load(save_filename)


