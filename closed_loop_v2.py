#coding=utf8


############## Instituto Federal de Brasília - Campus Taguatinga
############## Software para controle em malha fechada do Sistema de Tanques da QUANSER
############## Autor: Werbet Luiz Almeida da Silva (werbethluizz@hotmail.com)
############## Data: Agosto de 2022


from array import array
import time
from datetime import datetime
from quanser.hardware import HIL, HILError
import os

ref_cm=27
nivel_tanque_2 = 0.0
malha_fechada = True
sinal_malha_aberta = 3
referencia = ref_cm * (5 / 30)
kp = 6
ki = 2
tempo_amostragem = 0.05


#Congiguração das entradas analógicas do módulo Q8-USB
channels = array('I', [3, 6, 7]) #indica que as entradas 3,6 e 7 do Q8 serão utilizadas (3 e 6 para leitura dos nívels e 7 para a leitura da corrente na bomba
num_channels = len(channels)
buffer = array('d', [0.0] * num_channels)

#Congiguração das saídas analógicas do módulo Q8-USB
write_channels = array('I', [7]) # Indica que a saída analógia 7 será utilizada para acionamento da bomba
write_num_channels = len(write_channels)


digital_channel = array('I', [0,1]) #pinos digitais para habilitar o VOLTPAQ2
digital_num = len(digital_channel)
digital_buffer = array('b', [1,1]) 

card = HIL()

def main():
    erro_ant = 0
    erro = 0 
    u_max = 4
    u_min = -4
    u = 0
    i = 0
    

    try:
        card.open("q8_usb","0")
        #with open('data.csv', 'a+') as file:
         #   file.write(f'DataHora;Referencia;Nivel;Erro;Sinal_de_Controle;Corrente_na_Bomba\n')
        while True:
            print('########## Instituto Federal de Brasília ##########')
            print('########## Sistema de Tanques da Quanser ##########')
            print('########## Autor: Werbet L. A. Silva ##############')
            print('########## Agosto de 2022 #########################')
            print('')
            print('')

           
            start = datetime.now()
            nivel_tanque_1, nivel_tanque_2, corrente_bomba = leia()
            
            
            erro = referencia - nivel_tanque_2
                 
                
            print("Erro: ", round(erro, 2))
            print("Erro ant: ", round(erro_ant, 2))

            #Controlador:
            if malha_fechada:
                u = kp * erro + ki * erro_ant
            else:
                u = sinal_malha_aberta
            erro_ant = erro_ant + erro

            if erro_ant > 3: #limitador da parcela intergrativa positiva
                erro_ant = 3
            if erro_ant < -3: #limitador da parcela intergrativa positiva
                erro_ant = -3
           
            print('Sinal de controle antes: ', round(u,2))
            
                

            aplica_controle(u)
            trava(nivel_tanque_1,nivel_tanque_2, u)
           

            time.sleep(tempo_amostragem) #define o intervalo de amostragem
            os.system('cls') #para limpar a tela
            #with open('data.csv', 'a+') as file:
             #   file.write(f'{datetime.now()};{ref_cm};{nivel_tanque_2_new:.2f};{erro_new:.2f};{u:.2f};{corrente_bomba:.2f}\n')
            
                
                
                
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
    if (sinal_controle <= -2):
        sinal_controle = -2
    print('Sinal de controle depois: ', round(sinal_controle, 2))

    write_buffer = array('d', [sinal_controle]) 
    card.write_digital(digital_channel, digital_num, digital_buffer) #Garante que o canal do VoltPAQ vai estar ativo
    card.write_analog(write_channels, write_num_channels, write_buffer)

            
def trava(level_1: float, level_2: float, control_signal: float):  #Se o sinal de controle por positivo e atingir o limite máximo, desliga a bomba e para o programa
    #Assim como se o sinal de controle for negativo e atingir o limite mínimo
    print('Trava ativa!')
    if control_signal < 0 and level_2 < 0.5:
        desligar_bomba()
        print('NÍVEL CRÍTICO INFERIOR ATINGIDO - software interrompido por segurança!!!')
        exit()
    if control_signal > 0 and level_2 >= 5:
        desligar_bomba()
        print('NÍVEL CRÍTICO SUPERIOR DO TANQUE 2 ATINGIDO - software interrompido por segurança!!!')
        exit()
    if control_signal > 0 and level_1 >= 5:
        desligar_bomba()
        print('NÍVEL CRÍTICO SUPERIOR DO TANQUE 1 ATINGIDO - software interrompido por segurança!!!')
        exit()
    
def desligar_bomba():
     write_buffer = array('d', [0])
     card.write_digital(digital_channel, digital_num, digital_buffer)
     card.write_analog(write_channels, write_num_channels, write_buffer)

def leia():
    card.read_analog(channels, num_channels, buffer)
    nivel_tanque_1 = buffer[0]
    nivel_tanque_2 = buffer[1]
    corrente_bomba = buffer[2]
    print('Nivel tanque 1: ', round(nivel_tanque_1, 2))
    print('Nivel tanque 2: ', round(nivel_tanque_2, 2))
    print('Corrente na bomba: ', round(corrente_bomba, 2))

    if nivel_tanque_1 == 0.0 and nivel_tanque_2 == 0.0 and corrente_bomba == 0.0:
        desligar_bomba()
        print('Erro: erro na aquisição dos sinais analógicos')
        exit()
    return nivel_tanque_1, nivel_tanque_2, corrente_bomba

if __name__ == "__main__":
    main()


    
