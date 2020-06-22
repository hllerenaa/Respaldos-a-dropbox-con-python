import sys
import os
from glob import glob
import dropbox
import telebot
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError, AuthError
from datetime import datetime, date, time
from pathlib import Path

TOKEN = ''  # TOKEN DE DROPBOX
dbx = dropbox.Dropbox(TOKEN) # LOGEO A DROPBOX CON TOKEN
hora = datetime.now().time()
BACKUPPATH = "/{} {}:{}/".format(str(date.today()), hora.hour, hora.minute) # REPOSITORIO DE DESTINO SE CREARA BAJO ESTA ESTRUCTURA /FECHA HORA/

# FUNCION PARA BUSCAR ARCHIVOS EN ESTE CASO MIS BACKUPS SON .TAR
def ls(expr='*.tar'):
    return glob(expr)

# FUNCION PARA SUBIR ARCHIVOS A DROPBOX
def backup():
    TOKEN_TELEGRAM = ''  # AÑADIR TOKEN DE TELEGRAM
    tb = telebot.TeleBot(TOKEN_TELEGRAM) # CONEXION CON TELEGRAM
    chatid = '' # ID DE CHAT AL QUE QUIERE ENVIARLE EL MENSAJE EL BOT
    fecha_hora = "{} {}:{}".format(str(date.today()), hora.hour, hora.minute)
    for LOCALFILE in ls(): # BUSCARA EN EL DIRECTORIO ACTUAL TODOS LOS ARCHIVOS .TAR Y LOS RECORRERA APENAS ENCUENTRE
        with open(LOCALFILE, 'rb') as f:
            print("ARCHIVO " + LOCALFILE + " DESTINO " + BACKUPPATH + "...")
            try:
                p = Path(LOCALFILE) # OBTENER NOMBRE DE ARCHIVO ENCONTRADO EXCLUYENDOLE EL .TAR
                dbx.files_upload(f.read(), BACKUPPATH + ' ' + p.stem + '.tar',
                                 mode=WriteMode('overwrite')) #SUBIR ARCHIVOS A DROPBOX , PRIMER PARAMETRO ARCHIVO, SEGUNDO PARAMETRO LA RUTA MAS EL ARCHIVO Y SU FORMATO
            except ApiError as err: # EN CASO DE ERRORES
                if (err.error.is_path() and
                        err.error.get_path().reason.is_insufficient_space()):
                    sys.exit("ERROR: No se puede subir respaldos, espacio insuficiente.")
                    texto = 'No se puede subir respaldos, espacio insuficiente.'
                    tb.send_message(chatid, texto)
                elif err.user_message_text:
                    print(err.user_message_text)
                    tb.send_message(chatid, err.user_message_text) # MENSAJE A TELEGRAM EN CASO DE ERRORES
                    sys.exit()
                else:
                    print(err)
                    tb.send_message(chatid, err)
                    sys.exit()
    texto = '{} Respaldos subidos con exito.'.format(fecha_hora)
    tb.send_message(chatid, texto)  # MENSAJE A TELEGRAM SI EL PROCESO SE CUMPLE CON EXITO

# INIT PA EJECUTAR
try:
    dbx.users_get_current_account() # SE LOGEARA PRIMERO
    backup() # EJECUTARA LA FUNCION BACKUP
except AuthError:
    sys.exit("ERROR: Token de Dropbox Invalido.")
