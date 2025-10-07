import os
from dotenv import load_dotenv

load_dotenv()

# Configuración para Zoho Mail
radr = "yoandyc@zohomail.com"  # Tu email de Zoho
imapserver = "imap.zoho.com"    # Servidor IMAP de Zoho
smtpserver = "smtp.zoho.com"    # Servidor SMTP de Zoho  
smtpserverport = 465
pwd = os.getenv('ZOHO_PASSWORD')  # Contraseña de Zoho
sadr = "yoacv@nauta.cu"  # Email que puede enviar comandos
check_freq = 10  # Revisar cada 10 segundos