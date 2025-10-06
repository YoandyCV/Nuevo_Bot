from config import *
import imapclient
import imaplib
import pyzmail
import email.message
import smtplib
import time
from comandos import *

imaplib._MAXLINE = 1000000

def imap_init():
    print("Conectando IMAP... ", end='')
    global i
    i = imapclient.IMAPClient(imapserver)
    c = i.login(radr, pwd)
    i.select_folder("INBOX")
    print("Éxito.")

def smtp_init():
    print("Conectando SMTP...", end='')
    global s
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

def mail(text):
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

# Inicializar conexiones
imap_init()
smtp_init()

# Bucle principal corregido
while True:
    try:
        print("Esperando comandos...")
        msgs = get_unread()
        
        if msgs is None:
            time.sleep(check_freq)
            continue
            
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
                mail(t)
                continue
            else:
                print(f"Comando recibido: {cmds}")
                r = commands[cmds[0]](cmds)
                mail(str(r))
                print("Comando ejecutado")
                
        time.sleep(check_freq)
        
    except KeyboardInterrupt:
        print("Cerrando bot...")
        break
    except Exception as e:
        print(f"Error: {e}")
        # Reconectar después de error
        try:
            imap_init()
            smtp_init()
        except:
            print("Reconexión fallida, esperando...")
            time.sleep(10)

# Cerrar conexiones al final
try:
    i.logout()
    s.quit()
except:
    pass