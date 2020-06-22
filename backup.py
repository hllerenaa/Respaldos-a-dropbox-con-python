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
dbx = dropbox.Dropbox(TOKEN)
hora = datetime.now().time()
BACKUPPATH = "/{} {}:{}/".format(str(date.today()), hora.hour, hora.minute)


def ls(expr='*.tar'):
    return glob(expr)


def backup():
    TOKEN_TELEGRAM = ''  # AÑADIR TOKEN DE TELEGRAM
    tb = telebot.TeleBot(TOKEN_TELEGRAM)
    chatid = '1078235324'
    fecha_hora = "{} {}:{}".format(str(date.today()), hora.hour, hora.minute)
    for LOCALFILE in ls():
        with open(LOCALFILE, 'rb') as f:
            print("ARCHIVO " + LOCALFILE + " DESTINO " + BACKUPPATH + "...")
            try:
                p = Path(LOCALFILE)
                dbx.files_upload(f.read(), BACKUPPATH + ' ' + p.stem + '.tar',
                                 mode=WriteMode('overwrite'))
            except ApiError as err:
                if (err.error.is_path() and
                        err.error.get_path().reason.is_insufficient_space()):
                    sys.exit("ERROR: No se puede subir respaldos, espacio insuficiente.")
                    texto = 'No se puede subir respaldos, espacio insuficiente.'
                    tb.send_message(chatid, texto)
                elif err.user_message_text:
                    print(err.user_message_text)
                    tb.send_message(chatid, err.user_message_text)
                    sys.exit()
                else:
                    print(err)
                    tb.send_message(chatid, err)
                    sys.exit()
    texto = '{} Respaldos subidos con exito.'.format(fecha_hora)
    tb.send_message(chatid, texto)


try:
    dbx.users_get_current_account()
    backup()
except AuthError:
    sys.exit("ERROR: Token de Dropbox Invalido.")
