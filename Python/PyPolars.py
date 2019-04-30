import os, time
from functions.dtaFunctions import dtaFileHandler

base_path = r'L:\Documentos\00 SERVIÇOS\Polares Léo - 07-2016\MONITORAMENTO DISJ. LINHA\MONITORAMENTO 04'
file_name = 'Ensaio MONITORAMENTO 04_SAT_00.DTA'
file_path = os.path.join(base_path, file_name)

file = open(file_path, 'rb')
handler = dtaFileHandler(file)

t0 = time.time()
hasData = True
while hasData:
    hasData = not handler.read_block()

t1 = time.time()

print('Processado em ' + str(round(t1 - t0, 4)) + ' s\n')
handler.Data.plot_polars()