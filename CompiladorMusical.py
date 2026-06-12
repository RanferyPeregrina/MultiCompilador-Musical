import os
from mido import MidiFile

CarpetaMIDI = 'MIDIs'

# ArchivosMidi = [f for f in os.listdir(CarpetaMIDI) if f.lower().endswith('.mid')]
# for Archivo in ArchivosMidi:
#     print('\n'*5)
#     print(Archivo)
#     print('\n'*5)


from mido import MidiFile

def midi_num_to_note(num):
    nombres = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    octava = (num // 12) - 1
    return f"{nombres[num % 12]}{octava}"

mid = MidiFile('MIDIs/Fur Elise.mid')

tiempo_acumulado = 0.0
notas_activas = {}  # diccionario: {note_number: tiempo_inicio}

print(f"Canción: {mid.filename}")
print("Formato: tiempo_inicio_ms -> nota (duración_ms)")
print()

for msg in mid:
    tiempo_acumulado += msg.time
    
    # Note_on con velocity > 0 = inicio de nota
    if msg.type == 'note_on' and msg.velocity > 0:
        notas_activas[msg.note] = tiempo_acumulado
    
    # Note_off o note_on con velocity 0 = fin de nota
    elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
        if msg.note in notas_activas:
            inicio = notas_activas.pop(msg.note)
            duracion = tiempo_acumulado - inicio
            ms_inicio = int(inicio * 1000)
            ms_duracion = int(duracion * 1000)
            nota = midi_num_to_note(msg.note)
            print(f"{ms_inicio} ms -> {nota} (dura {ms_duracion} ms)")

# Al final, si quedan notas activas (MIDI mal cerrado)
for note, inicio in notas_activas.items():
    duracion = tiempo_acumulado - inicio
    print(f"{int(inicio*1000)} ms -> {midi_num_to_note(note)} (dura {int(duracion*1000)} ms, nota sin cierre)")