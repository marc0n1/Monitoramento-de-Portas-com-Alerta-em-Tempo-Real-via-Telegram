import socket
import threading
import time
import logging
from queue import Queue
import requests
from datetime import datetime

# Configurações do Telegram
TOKEN_TELEGRAM = "7766039404:AAGyBj-A7GhtEA8LfTUXx7o1NkovhUu9C1E"
CHAT_ID = "1904271548"
URL_BASE = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}"

# Logging
logging.basicConfig(
    filename='monitor_portas.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

NUM_THREADS = 50
TIMEOUT = 0.3
INTERVALO = 30
fila = Queue()
resultado_lock = threading.Lock()
monitorando = False
ultima_update_id = None
monitor_thread = None

# Funções principais
def enviar_telegram(token, chat_id, mensagem):
    url = f"{URL_BASE}/sendMessage"
    dados = {
        "chat_id": chat_id,
        "text": mensagem,
        "parse_mode": "Markdown"
    }
    try:
        resposta = requests.post(url, data=dados)
        if resposta.status_code != 200:
            print(f"Erro ao enviar mensagem: {resposta.text}")
    except Exception as e:
        print(f"Exceção no envio Telegram: {e}")

def escanear_porta(host, porta):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(TIMEOUT)
    resultado = sock.connect_ex((host, porta))
    sock.close()
    return resultado == 0

def trabalhador(host, resultado_scan):
    while True:
        porta = fila.get()
        if porta is None:
            break
        aberta = escanear_porta(host, porta)
        if aberta:
            with resultado_lock:
                resultado_scan.append(porta)
        fila.task_done()

def escanear_portas_multithread(host, portas):
    resultado_scan = []
    threads = []

    for _ in range(NUM_THREADS):
        t = threading.Thread(target=trabalhador, args=(host, resultado_scan))
        t.daemon = True
        t.start()
        threads.append(t)

    for porta in portas:
        fila.put(porta)

    fila.join()

    for _ in range(NUM_THREADS):
        fila.put(None)
    for t in threads:
        t.join()

    return resultado_scan

def formatar_portas(portas):
    portas_ordenadas = sorted(portas)
    return ", ".join(str(p) for p in portas_ordenadas)

# Função principal do monitoramento
def monitorar(host, portas, intervalo):
    global monitorando
    estado_anterior = escanear_portas_multithread(host, portas)
    logging.info(f"Início do monitoramento. Portas abertas inicialmente: {estado_anterior}")
    enviar_telegram(TOKEN_TELEGRAM, CHAT_ID, f"🚀 *Monitoramento iniciado* em `{host}`.\nPortas abertas: `{formatar_portas(estado_anterior)}`")

    while monitorando:
        time.sleep(intervalo)
        estado_atual = escanear_portas_multithread(host, portas)

        novas = [p for p in estado_atual if p not in estado_anterior]
        fechadas = [p for p in estado_anterior if p not in estado_atual]

        agora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if novas:
            msg = f"⚠️ *Novas portas abertas* em `{host}` às `{agora}`:\n`{formatar_portas(novas)}`"
            logging.warning(msg)
            enviar_telegram(TOKEN_TELEGRAM, CHAT_ID, msg)

        if fechadas:
            msg = f"❌ *Portas fechadas* em `{host}` às `{agora}`:\n`{formatar_portas(fechadas)}`"
            logging.info(msg)
            enviar_telegram(TOKEN_TELEGRAM, CHAT_ID, msg)

        estado_anterior = estado_atual

    enviar_telegram(TOKEN_TELEGRAM, CHAT_ID, f"🛑 *Monitoramento finalizado* para `{host}`.")

# Bot Telegram: escutar comandos
def escutar_comandos(ip_alvo, portas):
    global monitorando, ultima_update_id, monitor_thread

    while True:
        try:
            params = {"timeout": 30, "offset": ultima_update_id}
            resposta = requests.get(f"{URL_BASE}/getUpdates", params=params)
            if resposta.status_code != 200:
                print("Erro ao obter mensagens do Telegram")
                continue

            dados = resposta.json()
            for update in dados["result"]:
                ultima_update_id = update["update_id"] + 1
                mensagem = update.get("message", {})
                texto = mensagem.get("text", "")
                chat_id = mensagem.get("chat", {}).get("id")

                if chat_id != int(CHAT_ID):
                    continue

                if texto == "/start_monitor" and not monitorando:
                    monitorando = True
                    monitor_thread = threading.Thread(target=monitorar, args=(ip_alvo, portas, INTERVALO))
                    monitor_thread.start()
                    enviar_telegram(TOKEN_TELEGRAM, CHAT_ID, "🟢 *Monitoramento iniciado!*")

                elif texto == "/stop_monitor" and monitorando:
                    monitorando = False
                    enviar_telegram(TOKEN_TELEGRAM, CHAT_ID, "🔴 *Monitoramento será finalizado...*")

                elif texto == "/status":
                    status = "ativo" if monitorando else "inativo"
                    enviar_telegram(TOKEN_TELEGRAM, CHAT_ID, f"📡 Status atual do monitoramento: *{status}*")

        except Exception as e:
            print(f"Erro no loop de escuta de comandos: {e}")
            time.sleep(5)

# Execução principal
if __name__ == "__main__":
    ip_alvo = input("Digite o IP ou host a monitorar: ").strip()
    portas_monitorar = range(1, 1025)

    print("✅ Bot Telegram pronto para comandos: /start_monitor /stop_monitor /status")
    escutar_comandos(ip_alvo, portas_monitorar)
