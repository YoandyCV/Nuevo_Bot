import os
from dotenv import load_dotenv

load_dotenv()

# Configuración CORRECTA para Zoho Mail
radr =  "yoandyc.bot@gmail.com" # Email bot

imapserver = "imap.gmail.com"
smtpserver = "smtp.gmail.com"  
smtpserverport = 587
pwd = os.getenv('GMAIL_APP_PASSWORD')  # Contraseña de aplicación de Gmail
sadr = "yoacv@nauta.cu"
check_freq = 30