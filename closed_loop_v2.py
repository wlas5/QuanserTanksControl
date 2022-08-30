#coding=utf8


############## Instituto Federal de Brasília - Campus Taguatinga
############## Software para controle em malha fechada do Sistema de Tanques da QUANSER
############## Autor: Werbet Luiz Almeida da Silva (werbethluizz@hotmail.com)
############## Data: Agosto de 2022


from array import array
import time
from quanser.hardware import HIL, HILError

nivel_tanque_2 = 0.0
malha_fechada = True
referencia = 4
kp = 4
ki = 2

channels = array('I', [0, 1, 2]) #Entradas digitais
num_channels = len(channels)
buffer = array('d', [0.0] * num_channels)

write_channels = array('I', [0]) #write channel
write_num_channels = len(write_channels)
write_buffer = array('d', [3.7])

digital_channel = array('I', [0,1]) #pino digital para habilitar o VOLTPAQ2
digital_num = len(digital_channel)
digital_buffer = array('b', [1,0]) 

card = HIL()

def main():
    erro_ant = 0
    erro = 0 
    u_max = 4
    u_min = -4
    u = 0

    try:
        card.open("q8_usb","0")
        while True:
            nivel_tanque_1, nivel_tanque_2, corrente_bomba = leia()

            
            
            if malha_fechada:
                erro = referencia - nivel_tanque_2
            else:
                erro = 4

                
            print("Erro: ", erro)
            print("Erro ant: ", erro_ant)

            #Controlador:       
            u = kp * erro + ki * erro_ant
            #u = 3
            erro_ant = erro_ant + erro

            if erro_ant > 3: #limitador da parcela intergrativa positiva
                erro_ant = 3
            if erro_ant < -2: #limitador da parcela intergrativa positiva
                erro_ant = -2
           
            print('Sinal de controle antes: ', u)
            
            
          
            aplica_controle(u)
            trava(nivel_tanque_2, u)
            time.sleep(0.1)
            
    except HILError as e:
        print(e.get_error_message())
    except KeyboardInterrupt:
        desligar_bomba()
        print("Aborted by user.")
    finally:
        if card.is_valid():
            card.close()


def aplica_controle(sinal_controle: float):
    if (sinal_controle >= 4):
        sinal_controle = 4
    if (sinal_controle <= 0):
        sinal_controle = -2
    print('Sinal de controle depois: ', sinal_controle)
    write_buffer = array('d', [sinal_controle])
    card.write_digital(digital_channel, digital_num, digital_buffer)
    card.write_analog(write_channels, write_num_channels, write_buffer)

            
def trava(level_2: float, control_signal: float):  #Se o sinal de controle por positivo e atingir o limite máximo, desliga a bomba e para o programa
    #Assim como se o sinal de controle for negativo e atingir o limite mínimo
    print('Trava ativa!')
    if control_signal < 0 and level_2 < 0.5:
        desligar_bomba()
        exit()
    if control_signal > 0 and level_2 > 4.3:
        desligar_bomba()
        exit()
    
def desligar_bomba():
     write_buffer = array('d', [0])
     card.write_digital(digital_channel, digital_num, digital_buffer)
     card.write_analog(write_channels, write_num_channels, write_buffer)

def leia():
    card.read_analog(channels, num_channels, buffer)
    nivel_tanque_1 = buffer[1]
    nivel_tanque_2 = buffer[0]
    corrente_bomba = buffer[2]
    print('Nivel tanque 1: ', nivel_tanque_1)
    print('Nivel tanque 2: ', nivel_tanque_2)
    print('Corrente na bomba: ', corrente_bomba)

    if nivel_tanque_1 == 0.0 and nivel_tanque_2 == 0.0 and corrente_bomba == 0.0:
        desligar_bomba()
        print('Erro: erro na aquisição dos sinais analógicos')
        exit()
    return nivel_tanque_1, nivel_tanque_2, corrente_bomba

if __name__ == "__main__":
    main()


    