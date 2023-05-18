from iqoptionapi.stable_api import IQ_Option
import time


print('\n---- Login Projeto Trader ----\n')

print('E-mail: ', end='')
email = input()

print('Senha: ', end='')
senha = input()

API = IQ_Option('email', 'password')
API.connect()


end_from_time=time.time()
ANS=[]
for i in range(70):
    data = API.get_candles("EURUSD", 60, 1000, end_from_time)
    ANS = data+ANS
    end_from_time=int(data[0]["from"])-1
print(ANS)