from mido import MidiFile, MidiTrack, Message

# Crear un nuevo archivo y una pista
mid = MidiFile()
track = MidiTrack()
mid.tracks.append(track)

# Añadir un evento de cambio de instrumento (opcional, por defecto es piano)
# canal 0, programa 0 es Piano Acústico
track.append(Message('program_change', program=0, time=0))

# Notas a tocar (nota, velocidad/volumen, duración en ticks)
# Do central (60), Re (62), Mi (64)
notes = [60, 62, 64]

for note in notes:
    # Nota activada (note_on)
    track.append(Message('note_on', note=note, velocity=64, time=0))
    
    # Tiempo que dura la nota sonando (ej. 480 ticks)
    track.append(Message('note_off', note=note, velocity=64, time=480))

# Guardar el archivo MIDI
mid.save('mi_melodia.mid')
print("Archivo MIDI 'mi_melodia.mid' creado exitosamente.")