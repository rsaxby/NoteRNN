#!/usr/bin/env python
# -*- coding: utf-8 -*-

from music21 import *


class Song:
  '''
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
      nt = self.note_dict[nt]
      # takes in a str and creates a music21 note object
      if isinstance(nt, chord.Chord):
        # create midi event
        eventList = midi.translate.chordToMidiEvents(nt, includeDeltaTime=True)
        #add to midi track events
        for event in eventList:
          self.mt.events.append(event)       
        
      elif isinstance(nt, note.Note): 
        # create note
        # convert note to midi event
        eventList = midi.translate.noteToMidiEvents(nt, includeDeltaTime=True)
        for event in eventList:
          self.mt.events.append(event) # add midi event to the midi track

      elif isinstance(nt, note.Rest): 
        # get duration
        d_end = int(nt.duration.quarterLength) # must be int
        # create delta time events 
        dt1 = midi.DeltaTime(self.mt) 
        me1 = midi.MidiEvent(self.mt)
        dt1.time = 0 # start time = 0
        me1.type="DeltaTime"
        self.mt.events.append(dt1) # add dt event to mt
        dt2 = midi.DeltaTime(self.mt)
        me2 = midi.MidiEvent(self.mt)
        dt2.time = d_end # duration of delta time event
        me2.type="DeltaTime"
        self.mt.events.append(dt2) # add dt event to mt
                   
    # create event to end track
    self.end_track()
     # update events so they are all on this track
    self.mt.updateEvents()
    # create midi file to write
    mf = midi.MidiFile()
    mf.ticksPerQuarterNote = 424 #(higher=more notes)
    mf.tracks.append(self.mt)
    # write midi file
    print("Writing MIDI track")
    mf.open(file_path, 'wb')
    mf.write()
    mf.close()