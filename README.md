## Music Generation using a LSTM 

This was my first attempt at generating music using a LSTM network. 

### Contents

- Overview
  - Dataset
  - Preprocessing
  - Representation

### Overview

Being a performer, I was inspired to try to develop a model which could generate music. There are so many amazing models for music generation, such as [Magenta’s performance RNN](https://magenta.tensorflow.org/performance-rnn), [AIVA](https://www.aiva.ai/), and past OpenAI scholar Christine McCleavey’s project, [Clara](http://christinemcleavey.com/clara-a-neural-net-music-generator/). My (much more simplified) model drew inspiration from Magenta and Christine’s projects.

To start, however, I decided to take my simple character prediction RNN, and adapt it to predict notes. 

#### Dataset

I was working with piano MIDI files from the [Yamaha e-Piano Junior Competition](http://www.piano-e-competition.com/ecompetition/). I chose this dataset because it was recommended by Magenta for creating more dynamic and expressive pieces. Due to time and memory constraints, my dataset was limited to 330 songs. 

#### Preprocessing

I used [Music21](http://web.mit.edu/music21/doc/index.html) to process the MIDI files. Music21 stores MIDI events in streams, from which we can extract objects like Notes, Rests or Chords. I began by extracting each object from each song in the dataset. 

I stored each note sequentially in a list, and I also kept a dictionary of all music21 objects, which I later used to to retrieve the objects from using the generated notes. I pickled these files to be able to recreate a dataset from them in future sessions.  

#### Representation

The first iteration was single event (e.g. note, chord, rest) prediction - equivalent to a character-level RNN. The most recent iteration was my first attempt at implementing the time-shift employed by Magenta in their [Performance-RNN model](https://magenta.tensorflow.org/performance-rnn). I used Music21 to get all events within a designated time-shift (offset). However, due to time constraints, I was not able to process at the 10ms level, and instead I used 1 second intervals. 

Unfortunately, this did not produce very coherent songs; I achieved the best results by predicting 3 notes at a time. I think with more time and no memory constraints, I would like to continue to experiment with the time-shift technique. I'd also like to experiment with a CNN approach to music-generation. 

_Generated Music_

1. [Sample 1](gen_4_trimmed.m4a)
2. [Sample 2](gen_3_trimmed.m4a)
