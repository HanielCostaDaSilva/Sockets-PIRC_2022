#!/usr/bin/env python3
import socket
import os
TAM_MSG = 1024 # Tamanho do bloco de mensagem
HOST = '0.0.0.0' # IP do Servidor
PORT = 40000 # Porta que o Servidor escuta
'''
[0: comando
 1: Nome do Arquivo/Diretório
 2: Extra
 ]
 '''
def processa_msg_cliente(msg, con, cliente):
    msg = msg.decode()
    print('Cliente', cliente, 'enviou', msg)
    msg = msg.split()
    
    if msg[0].upper() == 'GET':
        nome_arq = " ".join(msg[1:])
        print('Arquivo solicitado:', nome_arq)
        try:
            status_arq = os.stat(nome_arq)
            arq = open(nome_arq, "rb")
            con.send(str.encode('+OK {}\n'.format(status_arq.st_size)))
            while True:
                dados = arq.read(TAM_MSG)
                if not dados: break
                con.send(dados)
            arq.close()
            return True
        except Exception as e:
            con.send(str.encode('-ERR {}\n'.format(e)))
    
    elif msg[0].upper() == 'LIST':
        lista_arq = os.listdir('.')
        con.send(str.encode('+OK {}\n'.format(len(lista_arq))))
        for nome_arq in lista_arq:
            if os.path.isfile(nome_arq):
                status_arq = os.stat(nome_arq)
                con.send(str.encode('arq: {} - {:.1f}KB\n'.format(nome_arq, status_arq.st_size/1024)))

            elif os.path.isdir(nome_arq):
                con.send(str.encode('dir: {}\n'.format(nome_arq)))
            else:
                con.send(str.encode('esp: {}\n'.format(nome_arq)))
        return True
    
    elif msg[0].upper() == 'QUIT':
        con.send(str.encode('+OK\n'))
        return False

    elif msg[0].upper()=='CWD':
        nome_dir = " ".join(msg[1:])
        print('Solicitação para entrar no diretório: ', nome_dir)

        try:
            os.chdir(nome_dir)
            con.send(str.encode('+OK Indo para: {}\n'.format(nome_dir)))

        except Exception as e:
            con.send(str.encode('-ERR {}\n'.format(e)))
        return True
    #== == == == Escreve Algo dentro de um arquivo.
    elif msg[0].upper()=='WRITE':
        nome_arq= "".join(msg[1])
        texto=" ".join(msg[2:])    
        print('Solicitação para escrever no arquivo: ', nome_arq)
        try:
            arquivo=open(nome_arq,'a')
            caracterRetorno=arquivo.write(texto)
            arquivo.close()

        except Exception as e:
            con.send(str.encode('-ERR {}\n'.format(e)))
        
        finally:
            con.send(str.encode('+OK Escrito: {}\n'.format(caracterRetorno)))

    else:
        con.send(str.encode('-ERR Invalid command\n'))
        return True

def processa_cliente(con, cliente):
    print('Cliente conectado', cliente)
    while True:
        msg = con.recv(TAM_MSG)
        if not msg or not processa_msg_cliente(msg, con, cliente): break
    
    con.close()
    print('Cliente desconectado', cliente)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serv = (HOST, PORT)
sock.bind(serv)
sock.listen(50)

while True:
    try:
        con, cliente = sock.accept()
    except: break
    processa_cliente(con, cliente)

sock.close()