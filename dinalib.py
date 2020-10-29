import numpy as np
import os.path
import scipy.signal as scs
from scipy.integrate import dblquad
from scipy import signal
from scipy.fft import fft, fftfreq
#import matplotlib.pyplot as plt
#import matplotlib
import json
import jsonschema
# TODO: fijarse que a veces los primeros X valores vienen malos
# TODO: estos 2 los tengo q meter en una función de corregir data

class DinaConfig():
    ''' Configuración Dinamometro
    input: configDina.json
    levanta datos de configuración del 
    dinamómetro
    '''
    
    def __init__(self, configPath):

        with open(configPath) as f:
            config = json.load(f)
        self.pozoID = config['Pozo']['ID']
        self.carrera = config['Pozo']['Carrera']
        self.span = (config['Celda']['PesoConocido2'] - config['Celda']['PesoConocido1'])/(config['Celda']['Referencia2']-config['Celda']['Referencia1'])
        self.offset = (config['Celda']['PesoConocido1'] - config['Celda']['Referencia1'])*self.span



class DinaProc(DinaConfig):
    ''' Dinamometer processing library
    input:
    data: string/list/array de datos de Fuerza y Acel
    samples: number of samples
    dtype: string datatype que viene en el Json
    Keyword arguments:
        splitchar = '' string separador en el array de Fza y Acc ej: (xxx;xxx)
        hopsize = 30  int porcion de muestra para la detección de un ciclo
    '''
    def __init__(self, configPath, data, samples, dtype='hexa', **kwargs):
        super(DinaProc, self).__init__(configPath)
        self.dtype = dtype    
        self.samples = samples
        self.splitchar = kwargs.get('splitchar', '')
        self.sample_rate = kwargs.get('sample_rate', 8)

    ######################
    ### Procesamiento ####
    ######################

        # Parseo de data de entrada en array (int)        
        if self.dtype == 'array':
            self.data_array = data
        else:
            self.data_array = self.dataToArray(data)  # Data array [ arra.Fza, arr.Acc]

        self.clean()
        
        # obtengo longitud de ciclo (fza y acc)
        self.cycle = self.getCycle(kwargs.get('hopsize', 100))
        # al ser distintos los ciclos me quedo con el de la fza
        # que parece ser mas estable (a mejorar)
        self.useCycle = self.cycle[1]
        # recorto el data array a la longitud del ciclo
        # por ahora me guio por el ciclo de la señal de fza
        # deberian ser iguales pero existe una diferencia
        self.cycle_data = np.copy(self.data_array[0:self.useCycle])
        # escalo fuerza
        self.scaled_cycle_data, self.max_f, self.min_f = self.scaleCycle() 
        
        # velocity
        self.centerData() # a la fuerza hay que centrarla antes de escalarla?

        self.vel = self.getVel(self.cycle_data.T[1])
        self.pos = self.getPos(self.vel)

        # escalar pos con carrera pico a pico 168 pulgadas

        

        # cambie el centrado por un hpf
        #self.centered = self.center()
        #self.cycle_data_fft , self.frec = self.FFT(self.centered, sr=self.sample_rate)
        

        # cycle_data centrada con un HPF
        self.cycle_data_fft , self.frec = self.FFT(self.cycle_data, sr=self.sample_rate)
        #self.scaled_cycle_data_fft, self.scaled_frec = self.FFT(self.center(self.scaled_cycle_data), sr=8)
        #self.cycle_data[:][1] = dblquad()
        
    

    def Half(self, strng):
        if len(self.splitchar)!=0:
            strng = strng.replace(self.splitchar,'')
        a = [ strng[:int(round(len(strng)/2))] , strng[int(round(len(strng)/2)):]  ]
        return a 
    # parsers

    def dataToArray(self, data):
        # Chequeo si viene en formato String
        # TODO: agregar para array o list
        if isinstance(data, str):
            # divido el string en cada , 
            # como si fuera un array
            if self.dtype == 'float':
                array = np.array([np.array(xi) for xi in data])
                return array
            else:
                data = data[1:-1].split(',')
                for a in range(len(data)):
                    data[a] = self.Half(data[a])
                    for b in range(len(data[a])):
                        if self.dtype == 'hexa':
                            data[a][b] = int(data[a][b], 16)
                        else:
                            # TODO: agregar para otros datatypes
                            pass
        array = np.array([np.array(xi) for xi in data])
        return array
        
    def getCycle(self, hopSize=100):
        # busca el ciclo buscando el error cuadratico medio 
        # en relacion a la primer porcion
        err = np.empty((len(self.data_array)-2*hopSize,2))
        for i in range(len(self.data_array)-2*hopSize):
            #for j in range(hopSize):
            #    e += (1/i)*sum(array[j]-array[hopSize+i+j])
            
            err[i] = (1/hopSize)*sum([(self.data_array[j]-self.data_array[hopSize+i+j])**2 for j in range(hopSize) ])

        min_idx = []
        min_idx = hopSize + err.argmin(axis=0)
        return min_idx
    
    def centerData(self):
        # centra la señal en cero.

        center_f = np.sum(self.cycle_data.T[0])/len(self.cycle_data.T[0])
        center_a = np.sum(self.cycle_data.T[1]/len(self.cycle_data.T[1]))
        self.cycle_data.T[0] = self.cycle_data.T[0] - center_f
        self.cycle_data.T[1] = self.cycle_data.T[1] - center_a

        pass

    def scaleCycle(self, a=0):
        # escala y limita sobre un ciclo de la señal
        # span = multiplicador, offset = threshold del limitador
        # a = parametro que define que señal se escala 

        minimo = self.offset + self.span*self.cycle_data[0,a]
        maximo = self.offset + self.span*self.cycle_data[0,a]
        array = np.empty(len(self.cycle_data))
        for i in range(len(self.cycle_data)):
            
            array[i] = self.offset + self.span*self.cycle_data[i,a]
            if minimo > array[i]:
                minimo = array[i]
            if maximo < array[i]:
                maximo = array[i]

        b, a = signal.butter(6, 6/(self.sample_rate/2), btype='low', analog=False)

        array = signal.filtfilt(b, a, array)

        return array, maximo, minimo
    
    def getArea(self):
        pass

    def clear_outlayers(self, dev):
        # TODO: el clear outlayers tiene qur ir buscando outlayers por partes, no de las 500 muestras en general
        # TODO: armar un mejor metodo para limpiar outlayers
                mean_f = np.mean(self.data_array.T[0])
                mean_a = np.mean(self.data_array.T[1])
                mean_dist_f = abs(self.data_array.T[0] - mean_f)
                mean_dist_a = abs(self.data_array.T[1] - mean_a)
                
                for a in range(len(self.data_array.T[0])):
                    if mean_dist_f[a] > dev*np.std(self.data_array.T[0]):
                        self.data_array.T[0,a] = mean_f
                    
                    if mean_dist_a[a] > dev*np.std(self.data_array.T[1]):
                        self.data_array.T[1,a] = mean_a 
        

    def clean(self, dev=2):
        # elimino outlayers 
        # habria q agregar algo de inteligencia para saber cuantas veces
        # hay que eliminar esos outlayers 
        self.clear_outlayers(dev=2*dev)
        self.clear_outlayers(dev=0.5*dev)
        self.clear_outlayers(dev=dev)
        self.clear_outlayers(dev=dev)
        pass

    def FFT(self, data, sr=None):
        if sr is None:
            sr = 1
            t = np.arange(0, self.useCycle)
        else:
            t = np.arange(0, self.useCycle)/sr
        
        b, a = signal.butter(6, 1/(self.sample_rate/2), btype='high', analog=False)
        
        
        fza_fft = fft(signal.filtfilt(b, a, data.T[0])) #/ t.shape
        #fza_fft = fft(data.T[0])
        acc_fft = fft(signal.filtfilt(b, a, data.T[1]))
        #acc_fft = fft(data.T[1])
        data_fft = np.array([fza_fft, acc_fft])

        
        #frec = t
        frec = fftfreq(self.useCycle, 1/sr)           
        return data_fft.T , frec

    def getPos(self, data):
        pos = [0]

        # Centro para eliminar la v inicial

        center_data = np.sum(np.array(data)/len(data))
        data = data - center_data

        for vel in data:
            pos.append(pos[-1] + vel/self.sample_rate)
        del pos[0]
        # La posición se mueve entre 0 y el maximo
        pos = pos - np.amin(pos)
        # escalo por la carrera
        pos *= (self.carrera/pos.max())
        return pos

    def getVel(self, data):
        vel = [0]
        
        for acc in data:
            vel.append(vel[-1] + acc/self.sample_rate)
        del vel[0]
        center_vel = np.sum(np.array(vel)/len(vel))
        vel = vel - center_vel

        return vel

    ### Ploteo
#     def plotFzaAcel(self):

#         fig = plt.gcf()
#         fig.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=0.5)
#         plt.subplot(211)
#         plt.plot(range(len(self.data_array)),self.data_array[:,0])
#         plt.axvline(self.cycle[0], color = 'g')
#         plt.title('Fuerza / Muestras')
#         plt.grid()
#         plt.subplot(212)
#         plt.plot(range(len(self.data_array)),self.data_array[:,1])
#         plt.axvline(self.cycle[1], color = 'g')
#         plt.title('Acel / Muestras')
#         plt.grid() 
#         plt.show()

#     def plotCycle(self):

#         fig = plt.gcf()
#         fig.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=0.5)
#         plt.subplot(311)
#         plt.plot(range(len(self.cycle_data)),self.cycle_data[:,0])
#         plt.axvline(self.cycle[0], color = 'g')
#         plt.title('Fuerza / Muestras')
#         plt.grid()
#         plt.subplot(312)
#         plt.plot(range(len(self.cycle_data)),self.scaled_cycle_data)
#         plt.axvline(self.cycle[0], color = 'g')
#         plt.title('Fuerza escalada / Muestras')
#         plt.grid()
#         plt.subplot(313)
#         plt.plot(range(len(self.cycle_data)),self.cycle_data[:,1])
#         plt.axvline(self.cycle[0], color = 'g')
#         plt.title('Acel / Muestras')
#         plt.grid() 
#         plt.show()

#     def plotAccVelPos(self):

#         fig = plt.gcf()
#         plt.plot(range(len(self.cycle_data)), self.cycle_data.T[1], linewidth=2.0, linestyle='--', label='acc')
#         plt.plot(range(len(self.cycle_data)), self.vel, linewidth=2.0, linestyle='dotted', label='vel')
#         plt.plot(range(len(self.cycle_data)), self.pos, linewidth=2.0, linestyle='-', label='pos')
#         plt.legend(loc='upper left',fontsize=12)
#         plt.title('ciclo de Aceleracion Fuerza y Posicion')
#         plt.xlabel('Samples')
#         plt.ylabel('Amp')
#         plt.grid() 
#         plt.show()

#     def plotFFT(self):
#         fig = plt.gcf()
#         #plt.plot(self.frec, np.abs(self.cycle_data_fft.T[0]), linewidth=2.0, linestyle='-', label='fza')
#         #plt.plot(self.scaled_frec, np.abs(self.scaled_cycle_data_fft))
#         plt.plot(self.frec, np.abs(self.cycle_data_fft.T[1]), color='g', linewidth=2.0, linestyle='-', label='acc')
#         plt.plot(self.frec, np.abs(fft(self.vel)), color='r', linestyle='-', label='vel' )
#         plt.plot(self.frec, np.abs(fft(self.pos)), color='b', linestyle='-', label='pos' )
#         plt.legend(loc='center right',fontsize=12)
#         plt.title('Magnitud acel / vel / pos DFT')
#         plt.xlim(0,7)
#         plt.xlabel('Samples')
#         plt.ylabel('Magnitud')
#         plt.grid() 
#         plt.show()

#     def plotFFT_bars(self):
#         w = 0.1
#         x = np.arange(len(self.frec))

#         fig, ax = plt.subplots()
#         rects1 = ax.bar(x - w/2, np.abs(self.cycle_data_fft.T[0]), w, label='fza')
#         rects2 = ax.bar(x + w/2, np.abs(self.cycle_data_fft.T[1]), w, label='acc')
#         plt.xlim(0,7)
#         ax.set_ylabel('Magnitud')
#         ax.set_xlabel('Frec')
#         ax.set_xticks(x)
#         ax.set_xticklabels(self.frec)
#         ax.legend()
#         fig.tight_layout()
#         plt.show()


#     def plotSuperficie(self):
#         fig = plt.gcf()
#         plt.plot(self.pos, self.scaled_cycle_data)
#         plt.grid()
#         plt.show()

        
# class DinaCartas(DinaProc):
#     def __init__(self):
#         pass

#     # ploteo grafico crudo fuerza y acel

#     # ploteo ciclo fuerza y posicion

#     # ploteo DFT

#     def PlotFzaAcel(self):

#         fig = plt.gcf()
#         fig.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=0.5)
#         plt.subplot(211)
#         plt.plot(range(len(self.data_array)),self.data_array[:,0])
#         plt.axvline(self.cycle[0], color = 'g')
#         plt.title('Fuerza / Muestras')
#         plt.grid()
#         plt.subplot(212)
#         plt.plot(range(len(self.data_array)),self.data_array[:,1])
#         plt.axvline(self.cycle[1], color = 'g')
#         plt.title('Acel / Muestras')
#         plt.grid() 
#         plt.show()
