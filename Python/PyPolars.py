import os

base_path = r'L:\Documentos\00 SERVIÇOS\Polares Léo - 07-2016\MONITORAMENTO DISJ. LINHA\MONITORAMENTO 01'
file_name = 'Ensaio MONITORAMENTO 01_SAT_00.DTA'
file_path = os.path.join(base_path, file_name)

def handleCase(ID, content):
    cases = {
        99: dta_date,
        1: dta_hit
    }

    func = cases.get(ID, not_defined)
    func(content)

def dta_date(content):
    print('Data: ' + str(content))

def dta_hit(content):
    print('HIT:')
    time = int.from_bytes(content[:6], byteorder='little')
    channel = content[6]
    print('Tempo: ' + str(time / 4E6))
    print('Canal: ' + str(channel))
    content = content[7:]


    print('\n')

def not_defined(content):
    pass

file = open(file_path, 'rb')

k = 0
times = []
while k < 1000:
    size = file.read(2)
    size = int.from_bytes(size, byteorder='little')
    ID = file.read(1)
    ID = int.from_bytes(ID, byteorder='little')
    content = file.read(size - 1)
    handleCase(ID, content)

    k += 1


