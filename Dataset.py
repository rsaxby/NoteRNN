#!/usr/bin/env python
# -*- coding: utf-8 -*-

from music21 import *
import pickle
import glob
import numpy as np

"""
Create a dataset of midi files.
	Args:
		data_dir (str): data directory for the midi files
		notes_fp (str): file path to save the notes to
		music21_objects_fp (str): file path to save the music21 objects to
		processed_fp (str): file path to save the list of processed files to
"""

class Dataset():
  def __init__(self, data_dir, notes_fp, music21_objects_fp, processed_fp):
    self.notes = [] # list of all extracted notes from songs (string form)
    self.music21_objects = {} # list of all note objects from songs
    self.unique_notes = None # set of unique notes
    self.data_dir = data_dir # data directory where midi files are stored/saved
    self.pitch2int = self.pitch_to_int() # dict of unique notes & chords
    self.int2pitch = {self.pitch2int[nt]:nt for nt in self.pitch2int} if self.pitch2int else None
    self.num_classes = None # num of unique notes
    self.encoded_notes = None # encoded notes
    self.notes_fp = notes_fp
    self.music21_objects_fp = music21_objects_fp
    self.processed_fp = processed_fp
    self.processed = [] # processed files
    
  # takes in a directory, extracts notes from all songs 
  # returns all notes in a single array
  def create_dataset(self):
    num_files = len([name for name in glob.glob(self.data_dir+"/*.MID")])
    count = 1
    for file in glob.glob(self.data_dir+"/*.MID"):
      print("\n{}/{} Processing {}...\n".format(count, num_files, file.strip(self.data_dir),))
      if file not in self.processed:
        # process the file
        try:
            # open midi file and chordify it
            mid = self.open_midi(file)
            # get a list of all the notes and chords in the file
            parts = instrument.partitionByInstrument(mid)
            m = parts.parts[0]
            # get 1/4 of the song length
            total_measures = len(m.measures(1,None)[1:])
            ms = m.measures(1,total_measures//4)
            mid = self.chordify_and_quantization(ms)
            self.extract_notes(mid)
            self.save_notes()
            self.processed.append(file)
        except:
            print("Could not process: {}".format(file))
        count += 1
      else:
        # already processed the file
        count += 1
    self.pitch_to_int()
    self.encode_notes()
    self.save_notes()    
  # reduce song length, chordify and quantize
  def chordify_and_quantization(self,mid):
    mid= mid.chordify().quantize(quarterLengthDivisors=[4])
    cr = analysis.reduceChords.ChordReducer()
    # get a list of all the notes and chords in the file
    parts = instrument.partitionByInstrument(mid)
    m = parts.parts[0]
    # None for end if full song
    ms = list(m.measures(1,12)[1:])
    ns = stream.Stream()
    for s in ms:
      for elem in s:
        if isinstance(elem, stream.Voice):
          n = cr.reduceMeasureToNChords(elem, 10)
          ns.append(n)
    return ns
     
  # extract notes from a midi file
  # return notes as string or note object
  def extract_notes(self, midi):
    notes_to_parse = None
    # get a list of all the notes and chords in the file
    parts = instrument.partitionByInstrument(midi)
    if parts: # if the file has instrument parts
      notes_to_parse = list(parts.parts[0].recurse())
    else: # file has notes in a flat structure
      notes_to_parse = midi.flat.notes
     
    for el in notes_to_parse:
      if isinstance(el, note.Rest):
        self.notes.append(el.name)
        # add music21 object to note dictionary
        self.music21_objects[el.name] = el
      elif isinstance(el, note.Note):
        self.notes.append(el.name)
        # add music21 object to note dictionary
        self.music21_objects[el.name] = el 
      elif isinstance(el, chord.Chord):
        self.notes.append(el.commonName)
        # add music21 object to note dictionary
        self.music21_objects[el.commonName] = el  
    
  # remove notes which are infrequent
  def denoise(notes, min_count=2):
    # create word counter
    notes_ = [note.name for note in notes]
    total_counts = Counter(notes_)
    # create filtered notes
    notes = [note for note in notes if total_counts[note.name] > min_count]
    return notes
  
  # open midi file
  def open_midi(self, file_name):
    return converter.parse(file_name)

  # save midi file
  def save_song(self, midi, file_name):
      midi.write('mid', fp=self.data_dir+file_name)

  # takes in a str and creates a music21 note object
  def create_note(self, note):
      return pitch.Pitch(note).midi
    
  # encode a note
  def pitch_to_int(self):
      # get unique pitch names
      self.unique_notes=sorted(set(item for item in self.notes))
      # map pitches to ints
      # note will be the key
      self.pitch2int = dict((note, number) for number, note in enumerate(self.unique_notes))
      self.num_classes = len(self.pitch2int)
  
  # encode notes in a song
  def encode_notes(self):
      encoded_notes = []
      # for each note in the song, encode it as an int, and add it to
      # the encoded list
      for i in range(0, len(self.notes)):
          encoded_notes.append(self.pitch2int[self.notes[i]])
      self.encoded_notes = np.array(encoded_notes)
      
  # save extracted notes and processed files as pickle
  def save_notes(self):
    """ create a pickle of an object """
    print("Saving notes...")
    pickle.dump(self.processed, open(self.processed_fp, "wb"))
    pickle.dump(self.notes, open(self.notes_fp,"wb"))
    pickle.dump(self.music21_objects, open(self.music21_objects_fp,"wb"))
    
  # create dataset from a pickled file
  def create_dataset_from_pickle(self):
    notes = self.load_pickled_file(self.notes_fp)
    music21_objects = self.load_pickled_file(self.music21_objects_fp)
    self.notes = notes
    self.music21_objects = music21_objects
    self.pitch_to_int()
    self.encode_notes()
    self.processed = self.load_pickled_file(self.processed_fp)
    
  def load_pickled_file(self,file_path):
    """ load a pickled file and return the object """
    pickled_file = open(file_path,"rb")
    data = pickle.load(pickled_file)
    return data
    
