#!/usr/bin/env python3
from flask import Flask
import threading
import os
import time
import logging
import imapclient
import imaplib
import pyzmail
import email.message
import smtplib

# Importar config aquí, a nivel de módulo
from config import *
from comandos import *

# Configuración Flask para Render
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Bot de Correo Activo - Render"

@app.route('/health')
def health():
    return "OK", 200

@app.route('/ping')
def ping():
    return "pong", 200

# Configuración IMAP
imaplib._MAXLINE = 1000000

# Variables globales para conexiones
i = None
s = None

def imap_init():
    global i
    print("Conectando IMAP... ", end='')
    i = imapclient.IMAPClient(imapserver)
    c = i.login(radr, pwd)
    i.select_folder("INBOX")
    print("Éxito.")

def smtp_init():
    global s
    print("Conectando SMTP...", end='')
    s = smtplib.SMTP(smtpserver, smtpserverport)
    c = s.starttls()[0]
    if c != 220:
        raise Exception('Conexión TLS fallida: ' + str(c))
    c = s.login(radr, pwd)[0]
    if c != 235:
        raise Exception('SMTP login fallido: ' + str(c))
    print("Éxito.")

def get_unread():
    uids = i.search(['UNSEEN'])
    if not uids:
        return None
    else:
        print("Encontrados %s sin leer" % len(uids))
        return i.fetch(uids, ['BODY[]', 'FLAGS'])

def analyze_msg(raws, a):
    try:
        msg = pyzmail.PyzMessage.factory(raws[a][b'BODY[]'])
        frm = msg.get_addresses('from')
        if not frm or frm[0][1] != sadr:
            print(f"Correo de {frm[0][1] if frm else 'desconocido'} - saltando")
            return None
            
        if msg.text_part is None:
            return None
            
        text = msg.text_part.get_payload().decode(msg.text_part.charset)
        text = text.strip()
        cmds = text.split(' ', 1)
        
        if len(cmds) == 1:
            cmds.append('')
            
        if cmds[0] not in commands:
            return False
            
        return cmds
    except Exception as e:
        print(f"Error analizando mensaje: {e}")
        return None

def send_mail(text):
    print("Enviando email...")
    msg = email.message.EmailMessage()
    msg["From"] = radr
    msg["To"] = sadr
    msg["Subject"] = "Respuesta Bot"
    msg.set_content(text)
    
    try:
        s.send_message(msg)
        print("Email enviado correctamente")
    except Exception as e:
        print(f"Error enviando email: {e}")

def run_bot():
    """Función principal del bot"""
    # Inicializar conexiones
    imap_init()
    smtp_init()
    
    # Bucle principal del bot
    while True:
        try:
            print("Revisando correos...")
            msgs = get_unread()
            
            if msgs:
                for a in msgs.keys():
                    if type(a) is not int:
                        continue
                    cmds = analyze_msg(msgs, a)
                    if cmds is None:
                        continue
                    elif cmds is False:
                        t = "Comando no válido. Los comandos son: \n"
                        for l in commands.keys():
                            t = t + str(l) + "\n"
                        send_mail(t)
                        continue
                    else:
                        print(f"Comando recibido: {cmds}")
                        r = commands[cmds[0]](cmds)
                        send_mail(str(r))
                        print("Comando ejecutado")
            
            time.sleep(check_freq)
            
        except Exception as e:
            print(f"Error en bucle principal: {e}")
            # Intentar reconectar
            try:
                if i:
                    i.logout()
                if s:
                    s.quit()
            except:
                pass
            time.sleep(30)
            try:
                imap_init()
                smtp_init()
            except Exception as reconect_error:
                print(f"Error reconectando: {reconect_error}")
                time.sleep(60)

def run_flask():
    """Ejecutar servidor web en puerto que Render espera"""
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 Iniciando servidor web en puerto {port}")
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == "__main__":
    print("🤖 Iniciando Bot de Correo...")
    
    # Iniciar bot en hilo separado
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    print("✅ Bot iniciado en segundo plano")
    print("🌐 Iniciando servidor web...")
    
    # Iniciar servidor web (principal para Render)
    run_flask()