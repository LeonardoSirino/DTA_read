import os
import time
from functions.dtaFunctions import dtaFileHandler
import tqdm
import tkinter as tk
from tkinter import filedialog

SAMPLE_RATE = 4E6 # Taxa de aquisição de 4 MHz. Atualizar esse valor para diferentes ensaios!!!!!

files = []

options = {}
options['initialdir'] = os.getcwd()
options['title'] = "Escolha o diretório de ensaio"
base_path = filedialog.askdirectory(**options)

all_files = os.listdir(base_path)
all_files = filter(lambda file_name : '.dta' in str.lower(file_name), all_files)
all_files = list(all_files)

test_name = base_path.split('/')[-1]
individual_dir = base_path + '/GRÁFICOS POLARES - ' + \
    test_name + '/POLARES INDIVIDUAIS/'
acumulated_dir = base_path + '/GRÁFICOS POLARES - ' + \
    test_name + '/POLARES ACUMULADOS/'
try:
    os.makedirs(individual_dir)
    os.makedirs(acumulated_dir)
except FileExistsError:
    pass

handler = dtaFileHandler()
handler.override_sample_rate(SAMPLE_RATE)
bar = tqdm.tqdm(total=len(all_files))
print('Inicio do processamento dos ' + str(len(all_files)) + ' arquivos\n')

files = all_files[:]
for file_name in files:
    print(file_name)
    handler.clear_data()
    file_path = os.path.join(base_path, file_name)
    file = open(file_path, 'rb')
    handler.set_file(file)

    t0 = time.time()
    hasData = True
    while hasData:
        hasData = not handler.read_block()

    t1 = time.time()

    # print(f'Processado em {t1 - t0: 0.4} s\n')
    handler.Data.init_polars()
    handler.Data.set_polars_export(
        individual_dir, acumulated_dir, file_name.split('.')[0])
    handler.Data.export_polars()
    handler.Data.reset_polars()

    bar.update()

bar.close()
