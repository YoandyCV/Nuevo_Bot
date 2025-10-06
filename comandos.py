import re
import requests

def echo(cmds):
    if len(cmds) < 2 or cmds[1].strip() == '':
        return "echo"
    else:
        return cmds[1]

def Buscador(cmds):
    if len(cmds) < 2 or cmds[1].strip() == '':
        return "Requiere de una palabra, frase o dirección web.\n/web Perros de raza\n/web https://dominio.com/abc"
    
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
        return f"Error en la búsqueda: {str(e)}"

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
        return f"Error accediendo a la web: {str(e)}"

commands = {
    "/echo": echo,
    "/web": Buscador
}