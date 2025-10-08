import re
import requests

def echo(cmds):
    """Comando público - cualquiera puede usar"""
    if len(cmds) < 2 or cmds[1].strip() == '':
        return "echo"
    else:
        return f"🔊 Eco: {cmds[1]}"

def Buscador(cmds):
    """Comando público - cualquiera puede usar"""
    if len(cmds) < 2 or cmds[1].strip() == '':
        return "❌ Requiere de una palabra, frase o dirección web.\n/web Perros de raza\n/web https://dominio.com/abc"
    
    string = cmds[1].strip()
    
    try:
        if string.startswith("http://") or string.startswith("https://"):
            resultado = BuscaWeb(string, True)
        else:
            resultado = BuscaWeb(string, False)
        
        # Limitar el tamaño para no exceder límites de email
        if len(resultado) > 10000:
            return resultado[:10000] + "\n\n... (contenido truncado)"
        return resultado
    except Exception as e:
        return f"❌ Error en la búsqueda: {str(e)}"

def BuscaWeb(string, Url_Bool):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        if Url_Bool:
            respuesta = requests.get(string, timeout=10, headers=headers)
        else:
            query = string.replace(' ', '+')
            respuesta = requests.get(f'https://google.com/search?q={query}', timeout=10, headers=headers)
        
        respuesta.raise_for_status()
        return respuesta.text
        
    except requests.RequestException as e:
        return f"❌ Error accediendo a la web: {str(e)}"

def help_command(cmds):
    """Comando público - muestra ayuda de todos los comandos"""
    help_text = """🤖 **COMANDOS DISPONIBLES** 🤖

📋 **Comandos Públicos** (todos pueden usar):

/help - Muestra esta lista de comandos disponibles con sus descripciones.

/echo [mensaje] - Retorna un mensaje de confirmación con eco. Si no se proporciona mensaje, devuelve 'echo'.

/web [argumento] - El argumento puede ser una palabra o frase de búsqueda en la web, o una URL directa a un sitio. 
   Ejemplos:
   /web gatos persa
   /web https://ejemplo.com

🛠️ **Comandos Administrativos** (solo para administradores):

/status - Muestra el estado actual del bot y información del sistema.

/admin_help - Muestra ayuda específica para comandos administrativos.

/list_users - [Futuro] Lista usuarios que han interactuado con el bot.

/block_user - [Futuro] Bloquea a un usuario específico.

---
💡 **Nota:** Los comandos administrativos solo pueden ser usados por el administrador del bot.
"""
    return help_text

# ✅ COMANDOS ADMINISTRATIVOS (solo para sadr)
def admin_status(cmds):
    """Comando admin - muestra estado del bot"""
    sender_email = cmds[2] if len(cmds) > 2 else "desconocido"
    return f"""🤖 **ESTADO DEL BOT**

✅ **Bot operativo**
📧 **Usuario actual:** {sender_email}
⚡ **Comando ejecutado:** {cmds[0]}
🕐 **Sistema:** Operativo

*Este comando solo está disponible para administradores.*"""

def admin_help(cmds):
    """Comando admin - ayuda administrativa"""
    return """🛠️ **AYUDA ADMINISTRATIVA**

**Comandos exclusivos para administradores:**

/status - Muestra el estado detallado del bot y métricas del sistema.

/admin_help - Muestra esta ayuda especializada.

/list_users - [En desarrollo] Lista todos los usuarios registrados.

/block_user [email] - [En desarrollo] Bloquea a un usuario específico.

/unblock_user [email] - [En desarrollo] Desbloquea a un usuario.

---
🔒 **Estos comandos requieren permisos de administrador.**"""

# ✅ DICCIONARIOS SEPARADOS
public_commands = {
    "/echo": echo,
    "/web": Buscador,
    "/help": help_command  # ✅ NUEVO COMANDO AQUÍ
}

admin_commands = {
    "/status": admin_status,
    "/admin_help": admin_help
}

# ✅ COMBINAR PARA FACIL ACCESO
commands = {**public_commands, **admin_commands}

# ✅ LISTA PARA VERIFICACIÓN RÁPIDA
admin_commands_list = list(admin_commands.keys())