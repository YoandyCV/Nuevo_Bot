import os
from dotenv import load_dotenv

load_dotenv()

# Configuración para Zoho Mail
radr = "yoandyc@zohomail.com" # Cambia por tu email de Zoho
imapserver = "imap.zoho.com"
smtpserver = "smtp.zoho.com"  
smtpserverport = 587
pwd = os.getenv('ZOHO_PASSWORD')  # Asegúrate de tener esta variable en Render
sadr = "yoacv@nauta.cu"
check_freq = 10