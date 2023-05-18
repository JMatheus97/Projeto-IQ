from iqoptionapi.stable_api import IQ_Option
import time
import json
import os
import sys
import threading
import schedule
from datetime import datetime, timedelta
from dateutil import tz
from colorama import init, Fore, Back
from tkinter import Tk
from tkinter.filedialog import askopenfilename


init(autoreset=True)
Tk().withdraw()
global ganhos
ganhos = 0
print('\n---- Login Projeto Trader ----\n')

print('E-mail: ', end='')
email = input()

print('Senha: ', end='')
senha = input()

API = IQ_Option('email', 'password')
API.connect()

while True:
    if API.check_connect() == False:
        print('Erro ao se conectar')
        API.connect()
    else:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(Fore.GREEN + 'Conectado com sucesso!\n\n'+Fore.RESET)
        break
    sleep(2)

def checkAgendamento():
    while True: 
        if API.check_connect() == False:
            API.connect()
        schedule.run_pending() 
        sleep(1) 

def stop(lucro, gain, loss):
    if loss.strip() != '':
        if lucro <= float('-' + str(abs(float(loss)))):
            print('Stop Loss batido!')
            sys.exit()

    if gain.strip() != '':
        if lucro >= float(abs(float(gain))):
            print('Stop Gain Batido!')
            sys.exit()

def compra (sinal, entrada):
    threading.Thread(target=verificaEntrada,args=(sinal, entrada, )).start()

def verificaEntrada(sinal, entrada):
    status, id = API.buy(int(entrada),sinal[1], sinal[2].lower(), int(sinal[3]))
    print('Entrada: ' + sinal[1] + ' - ' + sinal[2] +
          ' - ' + sinal[3] + 'min.\n Aguardando resultado...\n')
    if status:
        while True:
            status, valor = API.check_win_v3(id)
            if status:
                os.system('cls' if os.name == 'nt' else 'clear')
                print('Lucro: ' + (Fore.RED if valor < 0 else Fore.GREEN) + 'R$' + str(valor))
                break
    else:
        print(Fore.RED + '\n Erro ao realizar operação!\n' + Fore.RESET)


def timestamp_converter(x):  # Função para converter timestamp
    hora = datetime.strptime(datetime.utcfromtimestamp(
        x).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
    hora = hora.replace(tzinfo=tz.gettz('GMT'))
    return str(hora)[:-6]


def cataloga(par, dias, prct_call, prct_put, timeframe):
    data = []
    datas_testasdas = []
    sair = False
    s =  "03/01/2021"
    #time.mktime(datetime.strptime(s, "%d/%m/%Y").timetuple())
    time_ = time.mktime(datetime.strptime(s, "%d/%m/%Y").timetuple())
    while sair == False:
        velas = API.get_candles(par, (timeframe * 60), 1000, time_)
        velas.reverse()

        for x in velas:
            if datetime.fromtimestamp(x['from']).strftime('%Y-%m-%d') not in datas_testasdas:
                datas_testasdas.append(datetime.fromtimestamp(
                    x['from']).strftime('%Y-%m-%d'))

            if len(datas_testasdas) <= dias:
                x.update({'cor': 'verde' if x['open'] < x['close']
                          else 'vermelha' if x['open'] > x['close'] else 'doji'})
                data.append(x)
            else:
                sair = True
                break

        time_ = int(velas[-1]['from'] - 1)

    analise = {}

    for velas in data:
        horario = datetime.fromtimestamp(velas['from']).strftime('%H:%M')

        if horario not in analise:
            analise.update(
                {horario: {'verde': 0, 'vermelha': 0, 'doji': 0,  '%': 0, 'dir': ''}})

        analise[horario][velas['cor']] += 1

        try:
            analise[horario]['%'] = round(100 * (analise[horario]['verde'] / (
                analise[horario]['verde'] + analise[horario]['vermelha'] + analise[horario]['doji'])))
        except:
            pass

    for horario in analise:
        if analise[horario]['%'] > 50:
            analise[horario]['dir'] = 'CALL'
        if analise[horario]['%'] < 50:
            analise[horario]['dir'], analise[horario]['%'] = 'PUT ', (
                100 - analise[horario]['%'])

    return analise


operacao = 0
while operacao != 9:
    operacao = int(input(
        '\n ---- Menu Projeto Trader ----\n1 - Verificar sinais\n2 - Catalogador\n3 - AutoBot\n9 - Sair\n  :: '))

    if operacao == 1:  # Verificador
        os.system('cls' if os.name == 'nt' else 'clear')
        print(' ---- Verificador de Sinais ----')
        filename = askopenfilename()
        arquivo = open(filename, 'r').read()
        arquivo = arquivo.split('\n')
        print('Arquivo: ' + filename)
        print('Quantos Gales:\n0 - Sem Gale\n1 - 1 Gale\n2 - 2 Gales\n :: ', end='')
        gales = input()
        if not gales.isdigit():
            print('Digite apenas números!')
        else:
            win = 0
            loss = 0
            sinais = []
            for sinal in arquivo:
                if sinal.strip() != '':
                    dados = sinal.split(';')
                    sinais.append(dados)

            listaOrdenada = sorted(sinais, key=lambda sinal: str(datetime.now().strftime('%Y-%m-%d')) +' '+sinal[0])
            minList = list(filter(lambda sinal: datetime.strptime(
                str(datetime.now().strftime('%Y-%m-%d')) +' '+ sinal[0] + ':00', '%Y-%m-%d %H:%M:%S') < datetime.now(), listaOrdenada))
            for dados in minList:
                horario = datetime.strptime(
                    #str(datetime.now().strftime('%Y-%m-%d')) +' '+
                   '2021-01-03 ' + dados[0] + ':00', '%Y-%m-%d %H:%M:%S')
                horario = int(datetime.timestamp(horario))

                velas = API.get_candles(
                    dados[1].upper(), (int(dados[3]) * 60), 1, int(horario))

                if int(velas[0]['from']) == int(horario):
                    dir = 'call' if velas[0]['open'] < velas[0]['close'] else 'put' if velas[0]['open'] > velas[0]['close'] else 'doji'

                    if dir == dados[2].lower():
                        print(dados[0], dados[1], dados[2],
                            '|', Fore.GREEN + 'WIN')
                        win += 1
                    elif int(gales) != 0:
                        horario = datetime.strptime(
                            str(datetime.now().strftime('%Y-%m-%d')) +' '+dados[0] + ':00', '%Y-%m-%d %H:%M:%S')
                        horario = datetime.strptime(
                            str(horario + timedelta(minutes=int(dados[3]))), '%Y-%m-%d %H:%M:%S')
                        horario = datetime.timestamp(horario)

                        velas = API.get_candles(
                            dados[1].upper(), (int(dados[3]) * 60), 1, int(horario))

                        if int(velas[0]['from']) == int(horario):
                            dir = 'call' if velas[0]['open'] < velas[0]['close'] else 'put' if velas[0]['open'] > velas[0]['close'] else 'doji'

                            if dir == dados[2].lower():
                                print(dados[0], dados[1], dados[2],
                                    '|', Fore.GREEN + 'WIN')
                                win += 1
                            elif int(gales) == 2:
                                horario = datetime.strptime(
                                    str(datetime.now().strftime('%Y-%m-%d')) +' '+dados[0] + ':00', '%Y-%m-%d %H:%M:%S')
                                horario = datetime.strptime(
                                    str(horario + timedelta(minutes=int(dados[3]))), '%Y-%m-%d %H:%M:%S')
                                horario = datetime.timestamp(horario)

                                velas = API.get_candles(
                                    dados[1].upper(), (int(dados[3]) * 60), 1, int(horario))

                                if int(velas[0]['from']) == int(horario):
                                    dir = 'call' if velas[0]['open'] < velas[0]['close'] else 'put' if velas[0]['open'] > velas[0]['close'] else 'doji'

                                    if dir == dados[2].lower():
                                        print(dados[0], dados[1], dados[2],
                                            '|', Fore.GREEN + 'WIN')
                                        win += 1
                                    else:
                                        print(dados[0], dados[1], dados[2],
                                                '|', Fore.RED + 'LOSS')
                                        loss += 1
                            else:
                                print(dados[0], dados[1], dados[2],
                                    '|', Fore.RED + 'LOSS')
                                loss += 1
                    else:
                        print(dados[0], dados[1], dados[2],
                            '|', Fore.RED + 'LOSS')
                        loss += 1

                else:
                    print(dados[0], dados[1], dados[2], '|', Fore.RED +
                        'Não foi possivel pegar dados da vela!')

            print(20 * '-')
            print('Resultados')
            print('WINS: ' + Fore.GREEN + str(win))
            print('LOSS: ' + Fore.RED + str(loss))
            print('WINRATE: ' + str(round((win / (win+loss)) * 100)) + '%\n\n')

    elif operacao == 2:  # Catalogador
        os.system('cls' if os.name == 'nt' else 'clear')
        print(' ---- Catalogador de Sinais ----')

        print('Tipo da Opção: \n 1- Binaria\n 2- Digital\n :: ', end='')
        opcao = input()
        opcao = 'turbo' if int(opcao) == 1 else 'digital'

        print('Timeframe: ', end='')
        timeframe = int(input())

        print('Dias: ', end='')
        dias = int(input())

        print('Porcentagem: ', end='')
        porcentagem = int(input())

        print('Gales: ', end='')
        martingale = input()

        prct_call = abs(porcentagem)
        prct_put = abs(100 - porcentagem)

        p = API.get_all_open_time()

        catalogacao = {}
        for par in p[opcao]:
            if par != 'GBPJPY-OTC':
                if p[opcao][par]['open'] == True:

                    print(Fore.GREEN + '*' + Fore.RESET +
                          ' CATALOGANDO ' + par + '... ', end='')

                    catalogacao.update(
                        {par: cataloga(par, dias, prct_call, prct_put, timeframe)})

                    if martingale.strip() != '':
                        for horario in sorted(catalogacao[par]):
                            mg_time = horario
                            soma = {'verde': catalogacao[par][horario]['verde'], 'vermelha': catalogacao[par]
                                    [horario]['vermelha'], 'doji': catalogacao[par][horario]['doji']}

                            for i in range(int(martingale)):

                                catalogacao[par][horario].update(
                                    {'mg'+str(i): {'verde': 0, 'vermelha': 0, 'doji': 0,  '%': 0}})

                                mg_time = str(datetime.strptime((datetime.now()).strftime(
                                    '%Y-%m-%d ') + mg_time, '%Y-%m-%d %H:%M') + timedelta(minutes=timeframe))[11:-3]

                                if mg_time in catalogacao[par]:
                                    catalogacao[par][horario]['mg' + str(
                                        i)]['verde'] += catalogacao[par][mg_time]['verde'] + soma['verde']
                                    catalogacao[par][horario]['mg' + str(
                                        i)]['vermelha'] += catalogacao[par][mg_time]['verde'] + soma['vermelha']
                                    catalogacao[par][horario]['mg' + str(
                                        i)]['doji'] += catalogacao[par][mg_time]['verde'] + soma['doji']

                                    catalogacao[par][horario]['mg' + str(i)]['%'] = round(100 * (catalogacao[par][horario]['mg' + str(i)]['verde' if catalogacao[par][horario]['dir'] == 'CALL' else 'vermelha'] / (
                                        catalogacao[par][horario]['mg' + str(i)]['verde'] + catalogacao[par][horario]['mg' + str(i)]['vermelha'] + catalogacao[par][horario]['mg' + str(i)]['doji'])))

                                    soma['verde'] += catalogacao[par][mg_time]['verde']
                                    soma['vermelha'] += catalogacao[par][mg_time]['vermelha']
                                    soma['doji'] += catalogacao[par][mg_time]['doji']

                                else:
                                    catalogacao[par][horario]['mg' +
                                                              str(i)]['%'] = 'N/A'

                    print('Finalizado')

        print('\n\n')

        o = True
        for par in catalogacao:
            for horario in sorted(catalogacao[par]):
                ok = False
                msg = ''
                if catalogacao[par][horario]['%'] >= porcentagem:
                    ok = True
                else:
                    if martingale.strip() != '':
                        for i in range(int(martingale)):
                            if str(catalogacao[par][horario]['mg' + str(i)]['%']) != 'N/A':
                                if catalogacao[par][horario]['mg' + str(i)]['%'] >= porcentagem:
                                    ok = True
                                    break

                if ok == True:
                    msg = Fore.YELLOW + par + Fore.RESET + ' ; ' + horario + ' ; ' + (Fore.GREEN if catalogacao[par][horario]['dir'] == 'CALL' else Fore.RED) + catalogacao[par][horario]['dir'] + Fore.RESET + ' ; ' + str(
                        catalogacao[par][horario]['%']) + '% ; ' + Back.GREEN + Fore.BLACK + str(catalogacao[par][horario]['verde']) + Back.RED + str(catalogacao[par][horario]['vermelha']) + Back.RESET + Fore.RESET + str(catalogacao[par][horario]['doji'])

                    if martingale.strip() != '':
                        for i in range(int(martingale)):

                            if str(catalogacao[par][horario]['mg' + str(i)]['%']) != 'N/A':
                                msg += ' | MG ' + str(i+1) + ' ; ' + str(catalogacao[par][horario]['mg' + str(i)]['%']) + '% ; ' + Back.GREEN + Fore.BLACK + str(catalogacao[par][horario]['mg' + str(
                                    i)]['verde']) + Back.RED + str(catalogacao[par][horario]['mg' + str(i)]['vermelha']) + Back.RESET + Fore.RESET + str(catalogacao[par][horario]['mg' + str(i)]['doji'])
                            else:
                                msg += ' | MG ' + str(i+1) + ' - N/A - N/A'

                    print(msg)
                    open('sinais_' + '03-01_' + str(timeframe)+ 'M_' + str(porcentagem) +'%_'+ str(dias) + 'd_' +opcao.upper() +'.txt', 'a').write(horario + ';' + par + ';' + catalogacao[par][horario]['dir'].strip() + ';' + str(timeframe) + '\n')
                    if o:
                        o = False

    elif operacao == 3:  # AutoBot
        os.system('cls' if os.name == 'nt' else 'clear')
        print('---- AutoBot ----')
        filename = askopenfilename()
        arquivo = open(filename, encoding='UTF-8')
        print('Arquivo: ' + filename)
        lista = arquivo.read()
        arquivo.close
        print('Stop Loss: ', end='')
        stop_loss = input()
        print('Stop Gain: ', end='')
        stop_gain = input()
        print('Valor da entrada: ', end='')
        entrada = input()
        lista = lista.split('\n')

        for index, a in enumerate(lista):
            if a == '':
                del lista[index]
        sinais = []
        for sinal in lista:
            dados = sinal.split(';')
            sinais.append(dados)

        listaOrdenada = sorted(sinais, key=lambda sinal: sinal[0])
        minList = list(filter(lambda sinal: datetime.strptime(
            str(datetime.now().strftime('%Y-%m-%d')) +' '+ sinal[0] + ':00', '%Y-%m-%d %H:%M:%S') > datetime.now(), listaOrdenada))
        for sinal in minList:
            schedule.every().day.at(sinal[0]).do(compra, sinal=sinal, entrada=entrada)
        print('\nOperações agendadas!\n')
        threading.Thread(target=checkAgendamento).start()
    elif operacao == 9:
        print('Saindo..')
    else:
        print('Opção inválida!')
