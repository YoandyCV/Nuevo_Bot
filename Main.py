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
from datetime import datetime

# Importar config aquí, a nivel de módulo
from config import *
from comandos import *

# Configuración de logging detallado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("EmailBot")

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
    logger.info("🔄 Conectando IMAP...")
    i = imapclient.IMAPClient(imapserver)
    c = i.login(radr, pwd)
    i.select_folder("INBOX")
    logger.info("✅ IMAP conectado")

def smtp_init():
    global s
    logger.info("🔄 Conectando SMTP...")
    s = smtplib.SMTP(smtpserver, smtpserverport)
    c = s.starttls()[0]
    if c != 220:
        raise Exception('Conexión TLS fallida: ' + str(c))
    c = s.login(radr, pwd)[0]
    if c != 235:
        raise Exception('SMTP login fallido: ' + str(c))
    logger.info("✅ SMTP conectado")

def get_unread():
    uids = i.search(['UNSEEN'])
    if not uids:
        return None
    else:
        logger.info(f"📨 Encontrados {len(uids)} sin leer")
        return i.fetch(uids, ['BODY[]', 'FLAGS'])

def analyze_msg(raws, a):
    try:
        logger.debug(f"🔎 Analizando mensaje UID: {a}")
        msg = pyzmail.PyzMessage.factory(raws[a][b'BODY[]'])
        frm = msg.get_addresses('from')
        
        if not frm:
            logger.warning("❌ No se pudo obtener remitente")
            return None
            
        sender_email = frm[0][1]
        sender_name = frm[0][0]
        logger.info(f"📧 Email recibido de: {sender_name} <{sender_email}>")
            
        if msg.text_part is None:
            logger.warning("❌ Email sin parte de texto, buscando partes HTML...")
            if msg.html_part is not None:
                logger.info("✅ Encontrada parte HTML, usando esa")
                text = msg.html_part.get_payload().decode(msg.html_part.charset)
            else:
                logger.warning("❌ Email sin partes de texto ni HTML")
                return None
        else:
            text = msg.text_part.get_payload().decode(msg.text_part.charset)
            
        text = text.strip()
        logger.info(f"📝 Contenido del email ({len(text)} chars): '{text[:100]}{'...' if len(text) > 100 else ''}'")
        
        cmds = text.split(' ', 1)
        
        if len(cmds) == 1:
            cmds.append('')
            
        logger.info(f"🔍 Comando detectado: '{cmds[0]}' con argumentos: '{cmds[1]}'")
            
        # ✅ VERIFICAR SI EL COMANDO EXISTE
        if cmds[0] not in commands:
            logger.warning(f"❌ Comando no reconocido: '{cmds[0]}'. Comandos disponibles: {list(commands.keys())}")
            return False
            
        # ✅ VERIFICAR PERMISOS PARA COMANDOS ADMIN
        if cmds[0] in admin_commands_list and sender_email != sadr:
            logger.warning(f"🚫 Intento de uso de comando admin por usuario no autorizado: {sender_email}")
            return "PERMISSION_DENIED"
            
        logger.info(f"✅ Comando válido: {cmds[0]}")
        
        # ✅ AGREGAR EMAIL DEL REMITENTE PARA QUE LAS FUNCIONES SEPAN QUIÉN ESCRIBIÓ
        cmds.append(sender_email)
        return cmds
        
    except Exception as e:
        logger.error(f"❌ Error analizando mensaje: {e}")
        return None

def send_mail(text, to_email=None):
    """Función para enviar emails"""
    if to_email is None:
        to_email = sadr
    
    logger.info(f"📤 Enviando email a: {to_email}")
    try:
        msg = email.message.EmailMessage()
        msg["From"] = radr
        msg["To"] = to_email
        msg["Subject"] = "🤖 Respuesta Bot"
        msg.set_content(text)
        
        s.send_message(msg)
        logger.info("✅ Email enviado correctamente")
        return True
    except Exception as e:
        logger.error(f"❌ Error enviando email: {e}")
        return False

def run_bot():
    """Función principal del bot"""
    logger.info("🚀 Iniciando bot de correo...")
    
    # Contadores para estadísticas
    check_count = 0
    email_count = 0
    error_count = 0
    
    # Inicializar conexiones
    imap_init()
    smtp_init()
    
    logger.info("✅ Bot iniciado correctamente")
    
    # Bucle principal del bot
    while True:
        try:
            check_count += 1
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logger.info(f"🔄 Ciclo #{check_count} - {current_time}")
            
            msgs = get_unread()
            
            if msgs:
                logger.info(f"📨 Procesando {len(msgs)} emails nuevos")
                for a in msgs.keys():
                    if type(a) is not int:
                        logger.debug(f"⏭️ Saltando clave no entera: {a}")
                        continue
                        
                    email_count += 1
                    cmds = analyze_msg(msgs, a)
                    
                    if cmds is None:
                        logger.debug("⏭️ Mensaje saltado (None)")
                        continue
                    elif cmds is False:
                        logger.info("❌ Comando inválido detectado")
                        t = """❌ **Comando no reconocido**

El comando que enviaste no existe o tiene un error de escritura.

💡 **Sugerencia:** Usa el comando `/help` para ver la lista completa de comandos disponibles.

📋 **Comandos principales:**
/help - Muestra ayuda completa
/echo [mensaje] - Devuelve un eco
/web [búsqueda|url] - Busca en web o visita URL

*Si crees que esto es un error, verifica la ortografía del comando.*"""
                        # Obtener remitente del mensaje original
                        msg_data = msgs[a]
                        msg_obj = pyzmail.PyzMessage.factory(msg_data[b'BODY[]'])
                        frm = msg_obj.get_addresses('from')
                        sender_email = frm[0][1] if frm else sadr
                        send_mail(t, sender_email)
                        continue
                    elif cmds == "PERMISSION_DENIED":
                        logger.warning("🚫 Intento de acceso no autorizado a comando admin")
                        # Obtener remitente del mensaje original
                        msg_data = msgs[a]
                        msg_obj = pyzmail.PyzMessage.factory(msg_data[b'BODY[]'])
                        frm = msg_obj.get_addresses('from')
                        sender_email = frm[0][1] if frm else sadr
                        send_mail("🚫 No tienes permisos para ejecutar este comando administrativo", sender_email)
                        continue
                    else:
                        logger.info(f"🎯 Ejecutando comando: {cmds[0]}")
                        try:
                            r = commands[cmds[0]](cmds)
                            logger.info(f"✅ Comando ejecutado, respuesta: {len(str(r))} chars")
                            
                            # ✅ DETERMINAR QUIÉN RECIBE LA RESPUESTA
                            if cmds[0] in admin_commands_list:
                                # Comando admin: siempre responder a sadr
                                send_mail(str(r), sadr)
                                logger.info(f"📤 Respuesta admin enviada a {sadr}")
                            else:
                                # Comando público: responder al remitente original
                                sender_email = cmds[2] if len(cmds) > 2 else sadr
                                send_mail(str(r), sender_email)
                                logger.info(f"📤 Respuesta pública enviada a {sender_email}")
                                
                        except Exception as cmd_error:
                            logger.error(f"❌ Error ejecutando comando: {cmd_error}")
                            # Enviar error al remitente original
                            sender_email = cmds[2] if len(cmds) > 2 else sadr
                            send_mail(f"❌ Error ejecutando comando: {cmd_error}", sender_email)
            else:
                logger.debug("📭 No hay emails para procesar")
            
            # Estadísticas cada 10 ciclos
            if check_count % 10 == 0:
                logger.info(f"📊 Estadísticas - Ciclos: {check_count}, Emails: {email_count}, Errores: {error_count}")
            
            logger.debug(f"⏳ Esperando {check_freq} segundos...")
            time.sleep(check_freq)
            
        except KeyboardInterrupt:
            logger.info("🛑 Bot detenido por usuario")
            break
        except Exception as e:
            error_count += 1
            logger.error(f"💥 Error en bucle principal: {e}")
            
            # Intentar reconectar
            try:
                logger.info("🔄 Intentando reconexión...")
                if i:
                    i.logout()
                if s:
                    s.quit()
            except Exception as close_error:
                logger.error(f"❌ Error cerrando conexiones: {close_error}")
                
            time.sleep(30)
            
            try:
                logger.info("🔄 Re-inicializando conexiones...")
                imap_init()
                smtp_init()
                logger.info("✅ Reconexión exitosa")
            except Exception as reconect_error:
                logger.error(f"❌ Error en reconexión: {reconect_error}")
                time.sleep(60)

def run_flask():
    """Ejecutar servidor web en puerto que Render espera"""
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"🌐 Iniciando servidor web en puerto {port}")
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == "__main__":
    logger.info("🤖 Iniciando Bot de Correo en Render...")
    
    # Iniciar bot en hilo separado
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    logger.info("✅ Bot iniciado en segundo plano")
    
    # Iniciar servidor web (principal para Render)
    run_flask()