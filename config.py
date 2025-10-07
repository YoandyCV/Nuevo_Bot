import os
from dotenv import load_dotenv

load_dotenv()

# Configuración CORRECTA para Zoho Mail
radr =  "yoandyc@zohomail.com" # Tu email de Zoho
imapserver = "imap.zoho.com"
imapport = 993  # ⬅️ Puerto IMAP correcto
smtpserver = "smtp.zoho.com"  
smtpserverport = 465  # ⬅️ Puerto SMTP correcto
pwd = os.getenv('ZOHO_PASSWORD')
sadr = "yoacv@nauta.cu"
check_freq = 30