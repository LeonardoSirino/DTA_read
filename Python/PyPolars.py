import os, time
from functions.dtaFunctions import dtaFileHandler

base_path = r'L:\Documentos\00 SERVIÇOS\Polares Léo - 07-2016\MONITORAMENTO DISJ. LINHA\MONITORAMENTO 12'
file_name = 'Ensaio MONITORAMENTO 12_SAT_00 ao 05_linkados.DTA'
file_path = os.path.join(base_path, file_name)

export_dir = r'C:\Users\l01481\Desktop\teste'

file = open(file_path, 'rb')
handler = dtaFileHandler(file)

t0 = time.time()
hasData = True
while hasData:
    hasData = not handler.read_block()

t1 = time.time()

print('Processado em ' + str(round(t1 - t0, 4)) + ' s\n')
handler.Data.set_polars_export(export_dir, file_name[:-4])
handler.Data.export_polars()