import os
import numpy as np
import matplotlib.pyplot as plt


class dtaFileHandler:
    def __init__(self):
        self.IDs = []
        self.Data = dtaData()
        self.Config = dtaConfig()
        self.Config.set_sample_rate(4E6)  # Determinar esse valor pelo arquivo!
        self.num_hits = 0
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

    def set_file(self, file):
        self.file = file

    def clear_data(self):
        self.Data.reset_data()

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
        # print('Começo do ensaio')

    def __dta_hit(self, content):
        time = int.from_bytes(content[:6], byteorder='little')
        channel = content[6]
        data = content[7:]
        hit = Hit(channel, time, data)
        self.Data.add_hit(hit)
        self.num_hits += 1
        """
        if self.num_hits % 5000 == 0:
            os.system('cls')
            print('Hits identificados: ' + str(self.num_hits))
        """

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

        # print(IDs)

    def __dta_set_HDT(self, content):
        ch = content[0]
        HDT = content[1:]
        HDT = int.from_bytes(HDT, byteorder='little')
        # print('HDT de ' + str(HDT) + ' no canal ' + str(ch))

    def __dta_test_end(self, content):
        self.test_closed = True
        # os.system('cls')
        # print('Hits identificados: ' + str(self.num_hits))
        # print('Fim do ensaio')

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
    rate = 1

    def __init__(self, channel, time, content):
        self.raw_content = content
        self.params = {
            'ch': channel,
            'time': time / Hit.rate
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

    def set_sample_rate(self, rate):
        self.rate = rate
        Hit.rate = rate


class dtaData:
    def __init__(self):
        self.hits = []
        self.comments = []
        self.time_marks = []
        self.polar = None

    def add_hit(self, hit):
        self.hits.append(hit)

    def reset_data(self):
        self.hits = []
        self.comments = []
        self.time_marks = []

    def __str__(self):
        text = ''
        for hit in self.hits:
            text += hit.get_flat_data() + '\n'

        return text

    def export_polars(self):
        chs = self.get_param('ch')
        amps = self.get_param('Amp')
        times = self.get_param('time')

        data = np.vstack((chs, amps, times))
        data = data.transpose()

        for line in data:
            ch, amp, time = line
            self.polar.add_hit(ch, time, amp)

        self.polar.export()

    def set_polars_export(self, ind_dir, acu_dir, test_name):
        self.polar.ind_dir = ind_dir
        self.polar.acu_dir = acu_dir
        self.polar.test_number = test_name.split('_')[-1]

    def init_polars(self):
        if self.polar == None:
            polar = Polars()
            self.polar = polar

    def reset_polars(self):
        self.polar.reset_all_channels()

    def get_param(self, name):
        values = np.zeros(len(self.hits))
        for i, hit in enumerate(self.hits):
            values[i] = hit.params[name]

        return values


class polarChannel:
    def __init__(self, number):
        self.number = int(number)
        self.angs = np.linspace(0, 2 * np.pi, 360)
        self.counts = np.zeros(360)
        self.acu_counts = np.zeros(360)
        self.amps = np.zeros(360)
        self.acu_amps = np.zeros(360)

    def add_hit(self, amp, time):
        ang = (time / (1 / 60)) % 1
        ang *= 360
        self.counts[int(ang)] += 1
        self.acu_counts[int(ang)] += 1
        self.amps[int(ang)] += amp
        self.acu_amps[int(ang)] += amp

    def reset_data(self):
        self.counts = np.zeros(360)
        self.amps = np.zeros(360)


class Polars:
    def __init__(self):
        self.channels = []
        self.ch_nums = []
        self.min_count = 0
        self.ind_dir = ''
        self.acu_dir = ''
        self.test_number = ''

    def __new_channel(self, ch_num):
        channel = polarChannel(ch_num)
        self.channels.append(channel)
        self.ch_nums.append(ch_num)

    def get_channel(self, ch_num):
        if ch_num not in self.ch_nums:
            self.__new_channel(ch_num)

        index = self.ch_nums.index(ch_num)
        channel = self.channels[index]
        return channel

    def add_hit(self, ch, time, amp):
        channel = self.get_channel(ch)
        channel.add_hit(amp, time)

    def reset_all_channels(self):
        for channel in self.channels:
            channel.reset_data()

    def export(self):
        for channel in self.channels:
            if np.max(channel.counts) >= self.min_count:
                plt.polar(channel.angs, channel.counts)
                AcuAmpsNorm = channel.amps / \
                    np.max(channel.amps) * np.max(channel.counts)
                plt.polar(channel.angs, 0.5 * AcuAmpsNorm)
                title = 'Ch' + str(channel.number) + '_' + self.test_number
                plt.title(title)
                plt.legend(["Número de Hits", "Amplitude acumulada"])
                fig_name = title + ".png"
                fig_path = os.path.join(self.ind_dir, fig_name)
                plt.savefig(fig_path)
                plt.clf()

        for channel in self.channels:
            if np.max(channel.acu_counts) >= self.min_count:
                plt.polar(channel.angs, channel.acu_counts)
                AcuAmpsNorm = channel.acu_amps / \
                    np.max(channel.acu_amps) * np.max(channel.acu_counts)
                plt.polar(channel.angs, 0.5 * AcuAmpsNorm)
                title = 'Ch' + str(channel.number)
                plt.title(title)
                plt.legend(["Número de Hits", "Amplitude acumulada"])
                fig_name = title + ".png"
                fig_path = os.path.join(self.acu_dir, fig_name)
                plt.savefig(fig_path)
                plt.clf()

        legend = []
        for channel in self.channels:
            if np.max(channel.acu_counts) >= self.min_count:
                plt.polar(channel.angs, channel.acu_counts)
                legend.append('Canal ' + str(channel.number))

        plt.legend(legend)
        fig_name = 'Todos.png'
        fig_path = os.path.join(self.acu_dir, fig_name)
        plt.savefig(fig_path)
        plt.clf()
