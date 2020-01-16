import os
import time
from functions.dtaFunctions import dtaFileHandler
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import tqdm

files = []

SAMPLE_RATE = 4E6 # Taxa de aquisição de 4 MHz. Atualizar esse valor para diferentes ensaios!!!!!

def validate_file(file_name):
    names = file_name.split('.')
    is_dta_file = str.lower(names[-1]) == 'dta'
    is_cal_file = 'calibra' in str.lower(names[0])
    try:
        int(names[0].split('_')[-1])
        is_single_file = True
    except ValueError:
        is_single_file = False

    valid = is_dta_file
    return valid


def select():
    global files
    reslist = []
    selection = lstbox.curselection()
    for i in selection:
        entrada = lstbox.get(i)
        reslist.append(entrada)
    for val in reslist:
        files.append(val)

    main.quit()


options = {}
options['initialdir'] = os.getcwd()
options['title'] = "Escolha o diretório de ensaio"
base_path = filedialog.askdirectory(**options)

main = tk.Tk()
main.title("Escolha os arquivos para remover da análise")
main.geometry("+200+250")
frame = ttk.Frame(main, padding=(3, 3, 12, 12))
frame.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.E, tk.W))
lstbox = tk.Listbox(frame, selectmode=tk.MULTIPLE, width=50, height=25)
lstbox.grid(column=0, row=0, columnspan=2)

itens = os.listdir(base_path)
itens = filter(validate_file, itens)
all_files = []
for i, item in enumerate(itens):
    lstbox.insert(i, item)
    all_files.append(item)

btn = ttk.Button(frame, text="Ok", command=select)
btn.grid(column=1, row=1)

main.mainloop()

test_name = base_path.split('/')[-1]
individual_dir = base_path + '/GRÁFICOS POLARES - ' + \
    test_name + '/POLARES INDIVIDUAIS/'
acumulated_dir = base_path + '/GRÁFICOS POLARES - ' + \
    test_name + '/POLARES ACUMULADOS/'
os.makedirs(individual_dir)
os.makedirs(acumulated_dir)

for file_name in files:
    all_files.remove(file_name)

handler = dtaFileHandler()
handler.override_sample_rate(SAMPLE_RATE)
bar = tqdm.tqdm(total=len(all_files))
print('Inicio do processamento dos ' + str(len(all_files)) + ' arquivos\n')

files = all_files[:]
for file_name in files:
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
