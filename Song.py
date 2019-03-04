#!/usr/bin/env python
# -*- coding: utf-8 -*-

from music21 import *


class Song:
  '''
  Create and midi file from the generated notes.
	  Args:
		  generated_notes: list of notes (str) to be added to the midi file
		  note_dict: dict of music21 note objects from the trained network to convert our str notes to note objects
		  data_dir: directory to which we'll save the midi file
		  file_name: desired filename of the midi file
		  mt: to be Miditrack
		  d: duration (for midi events)
  '''
  def __init__(self, generated_notes, note_dict, data_dir, file_name):
    self.generated_notes = generated_notes
    self.note_dict = note_dict
    self.data_dir = data_dir
    self.file_name = file_name
    self.mt = None
    self.d = 0

  def create_rest(self, nt):
    # split on the separator, retrieve the last rest
    rest = nt.split('$')[-1] 
    # retrieve the duration of the rest
    duration = self.note_dict[rest].duration.quarterLength
    return int(duration)
  
          
  # end midi track
  def end_track(self):
    # create delta time
    dt = midi.DeltaTime(self.mt)
    dt.time = 0 # end of track, dt=0
    self.mt.events.append(dt)
    # create end of track event
    me = midi.MidiEvent(self.mt)
    me.type = "END_OF_TRACK"
    me.channel = 1 # specify channel
    me.data =''  # must set data to empty string
    self.mt.events.append(me)
   
          
    # create a midi file using the generated notes
  def create_song(self):
    # initialize midi track
    self.mt = midi.MidiTrack(1)
    
    # where to save the file
    file_path = self.data_dir+self.file_name
    
    for nt in self.generated_notes:
      
      velocity = 0
      pitch_ = 0
      duration = 0
      
      # takes in a str and creates a music21 note object
      if "Note" in nt:
        note_ = self.note_dict[nt] # retrieve note object
        self.d = int(note_.duration.quarterLength) # retrieve duration
        # convert note to midi event
        eventList = midi.translate.noteToMidiEvents(note_, includeDeltaTime=True)
        for event in eventList:
          self.mt.events.append(event) # add midi event to the midi track
        
      elif "Rest" in nt: 
        # create rests
        self.d = self.create_rest(nt)
        # create delta time events 
        dt1 = midi.DeltaTime(self.mt) 
        me1 = midi.MidiEvent(self.mt)
        dt1.time = 0 # start time = 0
        me1.type="DeltaTime"
        self.mt.events.append(dt1) # add dt event to mt
        dt2 = midi.DeltaTime(self.mt)
        me2 = midi.MidiEvent(self.mt)
        dt2.time = self.d # duration of delta time event
        me2.type="DeltaTime"
        self.mt.events.append(dt2) # add dt event to mt

      else: 
        # get chord
        c = self.note_dict[nt] # retrieve music21 chord object
        self.d = int(c.duration.quarterLength) # retrieve duration
        # create midi event
        eventList = midi.translate.chordToMidiEvents(c, includeDeltaTime=True)
        #add to midi track events
        for event in eventList:
          self.mt.events.append(event)

                   
    # create event to end track
    self.end_track()
     # update events so they are all on this track
    self.mt.updateEvents()
    # create midi file to write
    mf = midi.MidiFile()
    mf.ticksPerQuarterNote = 424 #1024 default experiment with different timing (higher=more notes)
    mf.tracks.append(self.mt)
    # write midi file
    print("Writing MIDI track")
    mf.open(file_path, 'wb')
    mf.write()
    mf.close()
