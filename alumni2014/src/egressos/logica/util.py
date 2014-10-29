# encoding: UTF-8

from random import randint
ano_inicial = 1963


'''
Created on 17/09/2013

@author: rodrigo
'''
def getProximoAno():
    """
    Obtém um inteiro que representa o próximo seguinte ao ano atual
    """
    from datetime import datetime
    dataAtual = datetime.now()
    return dataAtual.year +1


#utils
def generate_key(n):

    palavra = 'Uabw7c4FdePnfghEGJijrkulvVmL2o3pqZNs165txyz9IDAB80XCHKMOQRSTWY'
    str_n = str(n)
    for i in range(8-len(str_n)):
        str_n = "0" + str_n

    nk = ""
    for i in range(1,81):
        if i % 10 == 0:
            a = i / 10
            nk += palavra[int(str_n[a-1])]
        else:
            nk += palavra[randint(0,61)]
    return nk


