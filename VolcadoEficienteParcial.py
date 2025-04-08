import serial
import pandas as pd
from time import strftime
import os
import time
import numpy as np
import plotly.express as px
from plyer import notification

limiteDA = 150000

linInf = 50
limSup = 200

Address = "C:/BSICoS/Maxim/Ensayos/Asad"

class ReadLine:
    def __init__(self, s):
        self.buf = bytearray()
        self.s = s
    
    def readline(self):
        i = self.buf.find(b"\n")
        if i >= 0:
            r = self.buf[:i+1]
            self.buf = self.buf[i+1:]
            return r
        while True:
            i = max(1, min(2048, self.s.in_waiting))
            data = self.s.read(i)
            i = data.find(b"\n")
            if i >= 0:
                r = self.buf + data[:i+1]
                self.buf[0:] = data[i+1:]
                return r
            else:
                self.buf.extend(data)

init_add = 0
start = time.time()
end = time.time()

Primera = True

def PrintGraphs(Data, Add):
    DownPrinting = 4
    InitAddr = int(Data.iloc[0,0][1:],16)
    Hour = int(np.round_(InitAddr / 6758400)-1)

    Titulo = "Hora "+str(Hour)+" de sueño"
    # fig = subplots.make_subplots(rows=1,shared_xaxes=True, subplot_titles=("PPG"))
    # fig['layout']['xaxis']['title']='Tiempo'

    # fig.append_trace(go.Line(x=Data.Tiempo_formato[1::DownPrinting], y=Data.Green_Count[1::DownPrinting],name = "Led Green"), row=1, col=1)
    # fig.append_trace(go.Line(x=Data.Tiempo_formato[::DownPrinting], y=Data.Red_Count[::DownPrinting],name = "Led Red"), row=1, col=1)
    # fig.append_trace(go.Line(x=Data.Tiempo_formato[::DownPrinting], y=Data.IR_Count[::DownPrinting],name = "Led IR"), row=1, col=1)
    # fig.append_trace(go.Line(x=Data.Tiempo_formato[::DownPrinting], y=Data.Modulo[::DownPrinting],name = "Modulo Ac"), row=1, col=1)


    fig = px.line(Data.iloc[1:,:], x="Tiempo", y="Green_Count", title=Titulo) 
    # fig = px.line(x=Data.Tiempo_formato[1::DownPrinting],, title='Life expectancy in Canada')
    fig.write_html(os.path.join(Address,"Ensayo_Hora_"+str(Hour)+"_.html"), auto_open=False)

    fig.show()

    # fig.write_html(os.path.join(Address,"Ensayo.html"), auto_open=False)
    
    print("FIN")

def CheckMSB(Datos, BaseL1, BaseL2, BaseL3, lin):
    L1 = BaseL1
    L2 = BaseL2
    L3 = BaseL3
    if (int(Datos.loc[lin,"L11"], 16)>limSup and int(Datos.loc[lin-1,"L11"], 16)<linInf):# and (np.abs(Datos.loc[lin-1,"dAccel_dt"])<limiteDA) and (np.abs(Datos.loc[lin,"dAccel_dt"])<limiteDA) and (np.abs(Datos.loc[lin+1,"dAccel_dt"])<limiteDA):
        L1 = L1-int("10000", 16)

    if (int(Datos.loc[lin-1,"L11"], 16)>limSup and int(Datos.loc[lin,"L11"], 16)<linInf):# and (np.abs(Datos.loc[lin-1,"dAccel_dt"])<limiteDA) and (np.abs(Datos.loc[lin,"dAccel_dt"])<limiteDA) and (np.abs(Datos.loc[lin+1,"dAccel_dt"])<limiteDA):
        L1 = L1+int("10000", 16)

    if (int(Datos.loc[lin-1,"L21"], 16)>limSup and int(Datos.loc[lin,"L21"], 16)<linInf):# and (np.abs(Datos.loc[lin-1,"dAccel_dt"])<limiteDA) and (np.abs(Datos.loc[lin,"dAccel_dt"])<limiteDA) and (np.abs(Datos.loc[lin+1,"dAccel_dt"])<limiteDA):
        L2 = L2+int("10000", 16)

    if (int(Datos.loc[lin,"L21"], 16)>limSup and int(Datos.loc[lin-1,"L21"], 16)<linInf):# and (np.abs(Datos.loc[lin-1,"dAccel_dt"])<limiteDA) and (np.abs(Datos.loc[lin,"dAccel_dt"])<limiteDA) and (np.abs(Datos.loc[lin+1,"dAccel_dt"])<limiteDA):
        L2 = L2-int("10000", 16)

    if (int(Datos.loc[lin-1,"L31"], 16)>limSup and int(Datos.loc[lin,"L31"], 16)<linInf):# and (np.abs(Datos.loc[lin-1,"dAccel_dt"])<limiteDA) and (np.abs(Datos.loc[lin,"dAccel_dt"])<limiteDA) and (np.abs(Datos.loc[lin+1,"dAccel_dt"])<limiteDA):
        L3 = L3+int("10000", 16)

    if (int(Datos.loc[lin,"L31"], 16)>limSup and int(Datos.loc[lin-1,"L31"], 16)<linInf):# and (np.abs(Datos.loc[lin-1,"dAccel_dt"])<limiteDA) and (np.abs(Datos.loc[lin,"dAccel_dt"])<limiteDA) and (np.abs(Datos.loc[lin+1,"dAccel_dt"])<limiteDA):
        L3 = L3-int("10000", 16)

    return L1, L2, L3
    
def Tratamiento15min_Ensayo4h(Ensayo,Add):
    DF_Ens = pd.DataFrame()

    Datos = Ensayo[0].str.split(',', expand=True)

    Datos = Datos.rename(columns = {0:"Addr", 1:"L11", 2:"L12", 3:"L21", 4:"L22", 5:"L31", 6:"L32",7:"Modulo1", 8:"Modulo2"})
    for c in ["FF","AA","CC","DD","EE"]:
        Datos = Datos[~((Datos["L11"]==c)& (Datos["L12"]==c)& (Datos["L21"]==c)& (Datos["L22"]==c)& (Datos["L31"]==c)& (Datos["L32"]==c)& (Datos["Modulo2"]==c)& (Datos["Modulo1"]==c))]

    DF_Ens = pd.concat([DF_Ens,Datos],axis = 0)
    print(DF_Ens.shape)

    # Time_final = int(DF_Ens.iloc[-1,1], 16)*int("100000000000000", 16) + int(DF_Ens.iloc[-1,2], 16)*int("1000000000000", 16) + int(DF_Ens.iloc[-1,3], 16)*int("10000000000", 16) + int(DF_Ens.iloc[-1,4], 16)*int("100000000", 16) + int(DF_Ens.iloc[-1,5], 16)*int("1000000", 16) + int(DF_Ens.iloc[-1,6], 16)*int("10000", 16) + int(DF_Ens.iloc[-1,7], 16)*int("100", 16) + int(DF_Ens.iloc[-1,8], 16)
                                                                         
    DF_Ens = DF_Ens.reset_index(drop=True)
    # DF_Ens["TimeTrial"] = np.concatenate((np.array([0,0,0]),np.linspace(0,Time_final/1000000,DF_Ens.shape[0]-4),np.array([0])))
    
    DF_Ens = DF_Ens.drop(DF_Ens.shape[0]-1,axis=0)

    DF_Ens = DF_Ens.reset_index(drop=True)


    print(DF_Ens.index[-1])
    print(DF_Ens.shape[0])

    Base_L1 = int(DF_Ens.loc[2,"L12"], 16)*int("10000", 16)
    Base_L2 = int(DF_Ens.loc[2,"L22"], 16)*int("10000", 16)
    Base_L3 = int(DF_Ens.loc[2,"L32"], 16)*int("10000", 16)
    Base_M = int(DF_Ens.loc[2,"Modulo1"], 16)*int("100", 16) + int(DF_Ens.loc[2,"Modulo2"], 16)

    DF_Ens.loc[2,"B1"] = Base_L1
    DF_Ens.loc[2,"B2"] = Base_L2
    DF_Ens.loc[2,"B3"] = Base_L3

    Green = []
    Red = []
    IR = []
    Modulo = []
    print("Arrays Created")

    Green.append(Base_L1)
    Green.append(Base_L1)
    Green.append(Base_L1)
    Red.append(Base_L2)
    Red.append(Base_L2)
    Red.append(Base_L2)
    IR.append(Base_L3)
    IR.append(Base_L3)
    IR.append(Base_L3)
    Modulo.append(Base_M)
    Modulo.append(Base_M)
    Modulo.append(Base_M)

    start = time.time()
    for lin in DF_Ens.index[3:]:

        Base_L1, Base_L2, Base_L3 = CheckMSB(DF_Ens, Base_L1, Base_L2, Base_L3, lin)

        Green.append(Base_L1 + int(DF_Ens.loc[lin,"L11"], 16)*int("100", 16) + int(DF_Ens.loc[lin,"L12"], 16)) #int(Datos.loc[lin,1], 16)*int("10000", 16) + 
        Red.append(Base_L2 + int(DF_Ens.loc[lin,"L21"], 16)*int("100", 16) + int(DF_Ens.loc[lin,"L22"], 16))
        IR.append(Base_L3 + int(DF_Ens.loc[lin,"L31"], 16)*int("100", 16) + int(DF_Ens.loc[lin,"L32"], 16))
        Modulo.append(int(DF_Ens.loc[lin,"Modulo1"], 16)*int("100", 16) + int(DF_Ens.loc[lin,"Modulo2"], 16))

    DF_Ens["Green_Count"] = Green
    DF_Ens["Red_Count"] = Red
    DF_Ens["IR_Count"] = IR
    DF_Ens["Modulo"] = Modulo
    print("Cuenta de LEDs hecha")
    # DF_Ens["dAccel_dt"] = pd.DataFrame(np.concatenate((np.array([0]),np.diff(DF_Ens["Modulo"])/DF_Ens.loc[4,"TimeTrial"])))
    end = time.time()

    print(end - start)

    DF_Ens = DF_Ens.reset_index(drop=True)
    f2 = 256/15
    DF_Ens.loc[:,"Tiempo"]= (DF_Ens.index/f2)
    DF_Ens = DF_Ens.reset_index(drop=True)
    
    start = time.time()
    Xaxis = []
    Hour_Split =[]
    for i in DF_Ens.index:

        mm, ss = divmod(DF_Ens.loc[i,"Tiempo"], 60)
        hh, mm= divmod(mm, 60)    
        Xaxis.append(str(int(hh))+":"+str(int(mm)).zfill(2)+":"+str(np.round(ss,3)))
        Hour_Split.append(int(hh))


    DF_Ens["Tiempo_formato"] = Xaxis
    DF_Ens["Hour_Split"] = Hour_Split
    end = time.time()
    print("Hour_Split Created")
    print(end - start)

    PrintGraphs(DF_Ens,str(Add))
    end = time.time()

    print("PrintGraphs Created")
    print(end - start)

def Tratamiento5min(Ensayo,Add):
    DF_Ens = pd.DataFrame()

    Datos = Ensayo[0].str.split(',', expand=True)

    Datos = Datos.rename(columns = {0:"Addr", 1:"L11", 2:"L12", 3:"L21", 4:"L22", 5:"L31", 6:"L32",7:"Modulo1", 8:"Modulo2"})
    for c in ["AA","BB","CC","DD","EE","FF","AC"]:
        Datos = Datos[~((Datos["L11"]==c)& (Datos["L12"]==c)& (Datos["L21"]==c)& (Datos["L22"]==c)& (Datos["L31"]==c)& (Datos["L32"]==c)& (Datos["Modulo2"]==c)& (Datos["Modulo1"]==c))]

    Datos = Datos[~((Datos["L11"]==0)& (Datos["L12"]==0)& (Datos["L21"]==0)& (Datos["L22"]==0)& (Datos["L31"]==c)& (Datos["L32"]==c)& (Datos["Modulo2"]==c)& (Datos["Modulo1"]==c))] #Quitar posible tiempo guardado
    Datos = Datos[~((Datos["L11"]=="4C")& (Datos["L21"]=="4D")& (Datos["L31"]=="4E"))] #Quitar posible linea de base

    DF_Ens = pd.concat([DF_Ens,Datos],axis = 0)
    print(DF_Ens.shape)
                                                                   
    DF_Ens = DF_Ens.reset_index(drop=True)
    

    Base_L1 = 0
    Base_L2 = 0
    Base_L3 = 0
    Base_M = int(DF_Ens.loc[2,"Modulo1"], 16)*int("100", 16) + int(DF_Ens.loc[2,"Modulo2"], 16)
    Green = []
    Red = []
    IR = []
    Modulo = []
    print("Arrays Created")

    Green.append(Base_L1)
    Red.append(Base_L2)
    IR.append(Base_L3)
    Modulo.append(Base_M)

    start = time.time()
    for lin in DF_Ens.index[1:]:

        Base_L1, Base_L2, Base_L3 = CheckMSB(DF_Ens, Base_L1, Base_L2, Base_L3, lin)

        Green.append(Base_L1 + int(DF_Ens.loc[lin,"L11"], 16)*int("100", 16) + int(DF_Ens.loc[lin,"L12"], 16)) #int(Datos.loc[lin,1], 16)*int("10000", 16) + 
        Red.append(Base_L2 + int(DF_Ens.loc[lin,"L21"], 16)*int("100", 16) + int(DF_Ens.loc[lin,"L22"], 16))
        IR.append(Base_L3 + int(DF_Ens.loc[lin,"L31"], 16)*int("100", 16) + int(DF_Ens.loc[lin,"L32"], 16))
        Modulo.append(int(DF_Ens.loc[lin,"Modulo1"], 16)*int("100", 16) + int(DF_Ens.loc[lin,"Modulo2"], 16))

    DF_Ens["Green_Count"] = Green
    DF_Ens["Red_Count"] = Red
    DF_Ens["IR_Count"] = IR
    DF_Ens["Modulo"] = Modulo
    print("Cuenta de LEDs hecha")
    # DF_Ens["dAccel_dt"] = pd.DataFrame(np.concatenate((np.array([0]),np.diff(DF_Ens["Modulo"])/DF_Ens.loc[4,"TimeTrial"])))
    end = time.time()

    print(end - start)
    fshamp2 = 256/15
    DF_Ens = DF_Ens.reset_index(drop=True)
    DF_Ens.loc[:,"Tiempo_segundos"]= (DF_Ens.index/fshamp2)
    DF_Ens = DF_Ens.reset_index(drop=True)
    
    
    InitAddr = int(DF_Ens.iloc[0,0][1:],16)
    Hour = np.round(InitAddr / 6758400)-1

    start = time.time()
    Xaxis = []
    Hour_Split =[]
    for i in DF_Ens.index:

        mm, ss = divmod(DF_Ens.loc[i,"Tiempo_segundos"], 60)
        hh, mm= divmod(mm, 60)    
        Xaxis.append(str(int(hh+Hour))+":"+str(int(mm)).zfill(2)+":"+str(np.round(ss,3)))
        Hour_Split.append(int(hh))


    DF_Ens["Tiempo"] = Xaxis
    DF_Ens["Hour_Split"] = Hour_Split
    end = time.time()
    print("Hour_Split Created")
    print(end - start)

    PrintGraphs(DF_Ens,str(Add))
    end = time.time()

    print("PrintGraphs Created")
    print(end - start)


while 1:
    try:
        
        init_add = 0

        Lista_Total = []

        serialPort = serial.Serial(  
            port="COM8", baudrate=115200, bytesize=8, timeout=None, stopbits=serial.STOPBITS_ONE
        )
        rl = ReadLine(serialPort)
        
        #921600
        #9600
        # 115200
        serialString = ""  

        lin = 0
        CogerMSB = False
        Base_L1 =0
        Base_L2 =0
        Base_L3 =0

        TiempoComputo = 0
        ContadorComputo = 0
        TiempoParon = 0
        ContadorParon = 0

        ContadorSamples = 0
        NumSamples = 0

        parcial = 0


        while 1:
            if serialPort.in_waiting > 0:

                serialString = serialPort.readline()

                # bytesToRead = serialPort.inWaiting()
                # serialString = serialPort.read(bytesToRead)
                # serialString = rl.readline()

                # end = time.time()
                # print("Readline: "+str(end - start))

                try:
                    Linea = serialString.decode("Ascii")

                    while Linea[0:3]=="WIP":
                        Linea = Linea[3:]

                    if Linea[0:5] == "Paron":
                        ContadorParon = ContadorParon + 1
                        idx = Linea.index(',')
                        num = int(Linea[idx+1:-1])
                        TiempoParon = TiempoParon + num
                        print("Media Paron (200ms): "+str(TiempoParon/ContadorParon))

                    if Linea[0:12] == "TimerComputo":
                        ContadorComputo = ContadorComputo + 1
                        idx = Linea.index(',')
                        num = int(Linea[idx+1:-1])
                        TiempoComputo = TiempoComputo + num
                        print("Media Tiempo Computo: "+str(TiempoComputo/ContadorComputo))                        

                    if Linea[0:6] == "numero":
                        ContadorSamples = ContadorSamples + 1
                        idx = Linea.index(',')
                        num = int(Linea[idx+1:-1])
                        NumSamples = NumSamples + num
                        print("Media Num samples: "+str(NumSamples/ContadorSamples))      

                    if Linea[0:9] == "Password?":
                        if serialPort.writable:
                            print("Writable")
                            serialPort.write(str.encode("Footshake"))

                    if Linea[0:9] == "Va por la":
                        print(Linea)
                        if Primera:
                            IniAdd = int(Linea[10:-1],16)-int("1000",16)
                            print(IniAdd)
                            Primera = False
                            start2 = time.time()-2
                            print("Empieza en la " +str(IniAdd) +" y con tiempo "+str(start2))

                        else:
                            FinAdd = int(Linea[10:-1],16)
                            # print(FinAdd)
                            # end2 = time.time()
                            print("Lleva "+str(FinAdd-IniAdd)+" en "+str(np.round(time.time()-start2,2))+". Quiere decir Frcuencia "+str(((FinAdd-IniAdd)/(time.time()-start2))/8))

                    if Linea[0:8] == "Volcando":
                        Primera=True
                        start = time.time()
                        end = time.time()
                        print(Linea)
                        parcial = 0            
                        name = Linea.index(',')
                        add = str(Linea[name+1:-1])
                        AddressLong = Address+"Ensayo_"+strftime("%h%d_%H%M")+"_AddFinal"+add
                        os.mkdir(AddressLong)
                        startV = time.time()

                    if Linea[0:16] == "Visualizacion 5s":
                        startV = time.time()

                        # print("Visualizacion")
                        print(Linea)
                        Datos = pd.DataFrame.from_dict(Lista_Total)
                        Lista_Total = []

                        Tratamiento5min(Datos,AddressLong)

                        endV = time.time()
                        print("Tiempo Visualizacion: "+str(endV-startV))

                    elif Linea[0:13] == "Visualizacion":
                        # startV = time.time()

                        # print("Visualizacion")
                        print(Linea)
                        Datos = pd.DataFrame.from_dict(Lista_Total)

                        Lista_Total = []

                        Tratamiento15min_Ensayo4h(Datos,AddressLong)
                        # Datos.to_pickle(AddressLong+"/"+strftime("%h%d_%H%M")+"_EnsParcial"+str(parcial)+"_Empi"+add+".pkl")

                        endV = time.time()
                        print("Tiempo Visualizacion: "+str(endV-startV))

                    if Linea[0:3] == "Led":
                        Primera = True 

                    if Linea[0:4] == "Dirf":
                        DirF = int(Linea[5:-1],16)           
                        print("DirF "+str(DirF))

                    if Linea[0:11] == "Fin volcado":
                        notification.notify(
                            title='Fin del volcado de datos',
                            message='Se han volcado los datos de '+str(np.round(DirF/8/256,1))+"h",
                            app_name = "Apnea_MAX_app",
                            app_icon = "C:/BSICoS/HeartICO.ico",
                            ticker = "ticker",
                            timeout = 60)
                        print("notificacion")


                    if Linea[0:9] == "Se espera":
                        parcial = parcial +1

                        Datos = pd.DataFrame.from_dict(Lista_Total)

                        idx = Linea.index(',')
                        fin_add = int(Linea[idx+1:-1],16)

                        Lista_Total = []

                        name = Datos.iloc[0,0].index(',')
                        add = str(Datos.iloc[0,0][:name])

                        print(Linea)

                        Datos.to_pickle(AddressLong+"/"+strftime("%h%d_%H%M")+"_EnsParcial"+str(parcial)+"_Empi"+add+".pkl")
                        print("Ha tardado en el parcial "+str(time.time()-end)+", y en el ensayo lleva "+str(time.time()-start))
                        print("Velocidad "+str(np.round(((fin_add-init_add)/(time.time()-end)),2))+" [B/s]")
                        end = time.time()
                        init_add = fin_add

                    elif Linea[0] == "D":
                        Lista_Total.append(Linea[:-2])

                    else:
                        print(Linea)

                except:
                    print("EXCEPT")
                    print("EXCEPT")
                    print("EXCEPT")
                    print(Linea)
                    pass

    except: 
        print("No USB connected")
        time.sleep(2)

        




