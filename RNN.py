#!/usr/bin/env python
# -*- coding: utf-8 -*-

import torch
import torch.nn as nn

import torch.nn as nn
class RNN(nn.Module):
  """ 
  Initialize the model.
    Args:
      input_size (int): number of inputs/vocab size
      output_size (int): number of outputs
      embedding_dim (int): embedding dimension (num of cols in embedding lookup table)
      hidden_dim (int): hidden dimension
      num_layers (int): number of layers in lstm
      dropout (float): probability of dropout (default=0.5)		
  """
	
  def __init__(self, input_size, output_size, embedding_dim, hidden_dim, num_layers, dropout=0.5):
    super(RNN, self).__init__()

    self.output_size = output_size
    self.hidden_dim = hidden_dim
    self.num_layers = num_layers
    

    # embedding layer
    self.embedding = nn.Embedding(input_size, embedding_dim)

    # lstm layer
    self.lstm = nn.LSTM(embedding_dim, hidden_dim, num_layers,
              dropout=dropout, batch_first=True)

    # dropout
    self.dropout = nn.Dropout(dropout)

    # fc layer
    self.fc1 = nn.Linear(hidden_dim, output_size)

  def init_hidden(self, batch_size):
    """ 
    Initialize hidden state
      Args:
        batch_size (int): batch size
      Returns:
        hidden (tuple): returns two tensors of size [num_layers x batch_size x hidden_dim]
    """
    weight = next(self.parameters()).data
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    hidden = (weight.new(self.num_layers, batch_size, self.hidden_dim).zero_().to(device),
    weight.new(self.num_layers, batch_size, self.hidden_dim).zero_().to(device))

    return hidden
  
  def forward(self, x, hidden):
    """
    Forward pass on the inputs and hidden state.
    Args:
      x (tensor): inputs
      hidden (tensors): hidden state
    Returns:
      output (tensor): output from sigmoid activation
      hidden (tensor): output from hidden state
    """
    batch_size = x.size(0) # num rows in inputs

    # embedding layer
    embeddings = self.embedding(x.long())

    # lstm
    output, hidden = self.lstm(embeddings, hidden)

    # stack the lstm outputs
    output = output.contiguous().view(-1, self.hidden_dim)

    # dropout
    output = self.dropout(output)

    # fc
    output = self.fc1(output)

    # reshape into (batch_size, seq_length, output_size)
    output = output.view(batch_size, -1, self.output_size)
    
    # we want our output to be the last batch of the labels
    output = output[:, -1]

    return output, hidden
