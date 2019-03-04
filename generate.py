#!/usr/bin/env python
# -*- coding: utf-8 -*-


import torch.nn.functional as F
import numpy as np
import torch

def generate(rnn, prime_id, int_to_vocab, sequence_length, train_on_gpu, predict_len=100, top_k=5):
    """
    Generate music using the neural network
    Args:
        rnn: trained network
        prime_id (int): the encoded note to start the first prediction
        int_to_vocab (dict): dictionary of integer keys to note values
        sequence_length (int) : the sequence length the net was trained on
        train_on_gpu (bool) : whether or not to use gpu
        predict_len (int): the length of notes to generate
    Returns:
        (str) the generated notes
    """
    rnn.eval()
    
    # create a sequence (batch_size=1) with the prime_id
    current_seq = np.full((1, sequence_length), 0)
    current_seq[-1][-1] = prime_id

    predicted = [int_to_vocab[prime_id]]
    gen_notes = predicted
    
    for _ in range(predict_len):
        if train_on_gpu:
            current_seq = torch.LongTensor(current_seq).cuda()
        else:
            current_seq = torch.LongTensor(current_seq)
        
        # initialize the hidden state
        hidden = rnn.init_hidden(current_seq.size(0))
        
        # get the output of the rnn
        output, _ = rnn(current_seq, hidden)
        # get the next word probabilities
        p = F.softmax(output, dim=1).data
        if(train_on_gpu):
            p = p.cpu() # move to cpu
         
        # use top_k sampling to get the index of the next word
        top_k = top_k
        p, top_i = p.topk(top_k)
        top_i = top_i.numpy().squeeze()
        
        # select the likely next word index with some element of randomness
        p = p.numpy().squeeze()
        word_i = np.random.choice(top_i, p=p/p.sum())
        
        # retrieve that word from the dictionary
        word = int_to_vocab[word_i]
        predicted.append(word)
        gen_notes.append(word)
        
        # the generated word becomes the next "current sequence" and the cycle can continue
        current_seq = np.roll(current_seq.cpu(), -1, 1)
        current_seq[-1][-1] = word_i
    return gen_notes