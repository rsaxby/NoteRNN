#!/usr/bin/env python
# -*- coding: utf-8 -*-

import torch.nn as nn
import matplotlib.pyplot as plt
import torch
import numpy as np

def forward_back_prop(rnn, optimizer, criterion, inp, target, hidden, clip=5):
	"""
	Forward and backward propagation on the neural network
	Args:
		rnn: model to be trained 
		optimizer: optimizer
		criterion: loss function
		inp (tensors): a batch of input to the neural network
		target (tensors): target output for the batch of input
	  clip (int)
	Returns:
	 	(tuple) : tuple of the loss and the latest hidden state tensor
	"""
	device = 'cuda' if torch.cuda.is_available() else 'cpu'

	# Creating new variables for the hidden state, otherwise
	# we'd backprop through the entire training history
	h_ = tuple([each.data for each in hidden])

	# move to gpu if possible
	inputs, target = inp.to(device), target.to(device)
	# zero accumulated gradients
	rnn.zero_grad()
	# forward pass
	outputs, hidden = rnn(inputs, h_)
	# calc loss
	loss = criterion(outputs, target)
	# backprop
	loss.backward() #retain_graph=True
	# batch loss
	batch_loss = loss.item()

	# clip grad to avoid exploding gradient
	nn.utils.clip_grad_norm_(rnn.parameters(), clip)
	# update weights
	optimizer.step()

	# return the loss over a batch and the hidden state produced by our model
	return batch_loss, hidden


def train_rnn(train_loader, rnn, batch_size, optimizer, criterion, n_epochs, show_every_n_batches=100, plot=True):
	batch_losses = []
	loss_history = []
	count = 0
	counter = []   
	rnn.train()

	print("Training for %d epoch(s)..." % n_epochs)
	for epoch_i in range(1, n_epochs + 1):
	    
	    # initialize hidden state
		hidden = rnn.init_hidden(batch_size)
	    
		for batch_i, (inputs, labels) in enumerate(train_loader, 1):
	        
	        # make sure you iterate over completely full batches, only
			n_batches = len(train_loader.dataset)//batch_size
			if(batch_i > n_batches):
				break
	        
	        # forward, back prop
			loss, hidden = forward_back_prop(rnn, optimizer, criterion, inputs, labels, hidden)          
	        # record loss
			batch_losses.append(loss)

	        # printing loss stats
			if batch_i % show_every_n_batches == 0:
				print('Epoch: {:>4}/{:<4}  Loss: {}\n'.format(epoch_i, n_epochs, np.average(batch_losses)))
				loss_history.append(np.average(batch_losses))
				count += show_every_n_batches
				counter.append(count)
				batch_losses = []
	if plot:
	    plt.plot(counter,loss_history)
	    plt.show()
	# returns a trained rnn
	return rnn
