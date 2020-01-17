import os
import time
from functions.dtaFunctions import dtaFileHandler

SAMPLE_RATE = 10E6 # Taxa de aquisição de 10 MHz. Atualizar esse valor para diferentes ensaios!!!!!

handler = dtaFileHandler()
handler.override_sample_rate(SAMPLE_RATE)

file_path = r'/home/sirino/Documents/Lactec/SE_CANDELARIA/Dados/Tecnova/TECNOVA_TUDO_DISP3/GIS230KV/SE_CANDELARIA_GIS_230KV-FASEC/SE_CANDELARIA_disp3_GIS_230KV-FASEC_PARTE1_test03.DTA'

handler.clear_data()
file = open(file_path, 'rb')
handler.set_file(file)

t0 = time.time()
hasData = True
while hasData:
    hasData = not handler.read_block()

t1 = time.time()

handler.Data.print_comments()

print(f'Processado em {t1 - t0: 0.4} s\n')


