# configuracion del bot

import os
from dotenv import load_dotenv

load_dotenv()

# Email que servira para el bot
radr =  "yoandyc.bot@gmail.com"

imapserver = "imap.gmail.com"
smtpserver = "smtp.gmail.com"  
smtpserverport = 587
pwd = os.getenv('GMAIL_APP_PASSWORD')  # Contraseña de aplicación de Gmail
sadr = "yoacv@nauta.cu"
check_freq = 30