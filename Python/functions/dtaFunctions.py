class dtaFileHandler:
    def __init__(self, file):
        self.file = file
        self.IDs = []
        self.Data = dtaData()
        self.Config = dtaConfig()
        self.AE_params = {
            1: (2, 'RiseTime'),
            2: (2, 'CountsToPeak'),
            3: (2, 'Counts'),
            4: (2, 'Energy'),
            5: (4, 'Duration'),
            6: (1, 'Amp'),
            7: (1, 'RMS'),
            8: (1, 'ASL'),
            9: (1, 'Gain'),
            10: (1, 'THR'),
            11: (1, 'Pre-Amp Curent'),
            12: (4, 'Lost Hits'),
            13: (2, 'Average Frequncy'),
            14: (2, 'Reserved'),
            15: (6, 'Reserved'),
            16: (4, 'Reserved')
        }

    def read_block(self):
        size = self.file.read(2)
        size = int.from_bytes(size, byteorder='little')
        ID = self.file.read(1)
        ID = int.from_bytes(ID, byteorder='little')
        self.add_ID(ID)
        content = self.file.read(size - 1)
        self.__handleBlock(ID, content)

        end = ID == 0

        return end

    def add_ID(self, ID):
        if ID not in self.IDs and ID != 0:
            self.IDs.append(ID)

    def __handleBlock(self, ID, content):
        cases = {
            99: self.__dta_date,
            1: self.__dta_hit,
            42: self.__dta_hw_setup,
            129: self.__dta_test_end,
            24: self.__dta_set_HDT,
            5: self.__dta_event_data_set_def
        }

        func = cases.get(ID, self.__dta_not_defined)
        func(content)

    def __dta_date(self, content):
        self.date = str(content)

    def __dta_hit(self, content):
        time = int.from_bytes(content[:6], byteorder='little')
        channel = content[6]
        data = content[7:]
        hit = Hit(channel, time, data)
        self.Data.add_hit(hit)

    def __dta_hw_setup(self, content):
        content = content[3:]  # Informações de versão do arquivo DTA
        IDs = []
        while len(content) > 0:
            size = content[:2]
            content = content[2:]
            size = int.from_bytes(size, byteorder='little')
            ID = content[0]
            data = content[1:size]
            self.__handleBlock(ID, data)

            if ID not in IDs:
                IDs.append(ID)

            content = content[size:]

        print(IDs)

    def __dta_set_HDT(self, content):
        ch = content[0]
        HDT = content[1:]
        HDT = int.from_bytes(HDT, byteorder='little')
        # print('HDT de ' + str(HDT) + ' no canal ' + str(ch))

    def __dta_test_start(self):
        self.test_started = True
        print('Começo do ensaio')

    def __dta_test_end(self, content):
        self.test_closed = True
        print('Fim de ensaio')

    def __dta_event_data_set_def(self, content):
        num_param = content[0]
        param_IDs = content[1:num_param + 1]
        self.test_params = param_IDs
        hit_struct = []
        for ID in param_IDs:
            aux = self.AE_params.get(ID)
            if aux != None:
                hit_struct.append(aux)

        self.Config.set_hit_structure(hit_struct)

        
    def __dta_not_defined(self, content):
        pass


class Hit:
    struct = []

    def __init__(self, channel, time, content):
        self.raw_content = content
        self.params = {
            'ch': channel,
            'time': time
            }
        self.__parseContent(content)
        
    def __parseContent(self, content):
        pointer = 0
        for param in Hit.struct:
            size, name = param
            data = content[pointer:pointer + size]
            data = int.from_bytes(data, byteorder='little')
            pointer += size
            self.params[name] = data

    def __str__(self):
        return self.get_flat_data()

    def get_flat_data(self):
        return str(self.params)


class Channel:
    def __init__(self, num):
        self.num = num

    def set_hdt(self, hdt):
        self.hdt = hdt


class dtaConfig:
    def __init__(self):
        self.channels = []
        self.channel_numbers = []

    def __new_channel(self, ch_num):
        if ch_num not in self.channel_numbers:
            channel = Channel(ch_num)
            self.channels.append(channel)
            self.channel_numbers.append(ch_num)

    def get_channel(self, ch_num):
        if ch_num not in self.channel_numbers:
            self.__new_channel(ch_num)

        index = self.channel_numbers.index(ch_num)
        channel = self.channels[index]

        return channel

    def set_hit_structure(self, struct):
        self.hit_struct = struct
        Hit.struct = struct


class dtaData:
    def __init__(self):
        self.hits = []
        self.comments = []
        self.time_marks = []

    def add_hit(self, hit):
        self.hits.append(hit)

    def __str__(self):
        text = ''
        for hit in self.hits:
            text += hit.get_flat_data() + '\n'

        return text
