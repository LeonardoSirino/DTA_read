import os
from functions.dtaFunctions import dtaFileHandler

base_path = r'L:\Documentos\00 SERVIÇOS\Polares Léo - 07-2016\MONITORAMENTO DISJ. LINHA\MONITORAMENTO 01'
file_name = 'Ensaio MONITORAMENTO 01_SAT_00.DTA'
file_path = os.path.join(base_path, file_name)

file = open(file_path, 'rb')
handler = dtaFileHandler(file)

hasData = True
while hasData:
    hasData = not handler.read_block()

print(handler.Data)