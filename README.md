
# 🔐 Monitor de Portas com Alertas via Telegram

Este é um projeto de monitoramento de portas em tempo real desenvolvido em Python. Ele escaneia continuamente as portas de um host e envia alertas via Telegram sempre que novas portas são abertas ou fechadas.

## ✅ Funcionalidades

- Monitoramento contínuo de portas TCP
- Alertas via Telegram em tempo real
- Multithreading para escaneamento rápido
- Comandos para iniciar e parar o monitoramento via Telegram
- Registro de logs em arquivo local

---

## 🛠 Requisitos

- Python 3.8 ou superior

### Bibliotecas necessárias

Instale com:

```bash
pip install requests
```

---

## ⚙️ Como usar

1. **Configure o Token e o Chat ID do Telegram:**

No início do código, substitua pelas suas credenciais:

```python
TOKEN_TELEGRAM = "SEU_TOKEN_AQUI"
CHAT_ID = "SEU_CHAT_ID_AQUI"
```

2. **Execute o script:**

```bash
python monitor_portas.py
```

3. **Controle via Telegram:**

- Envie `/start_monitor` para iniciar o monitoramento
- Envie `/stop_monitor` para parar o monitoramento

---

## 🔧 Personalização

- **Intervalo entre varreduras:** por padrão, é de 30 segundos. Você pode alterar a constante `INTERVALO` no código.
- **Faixa de portas escaneadas:** por padrão, vai de 1 a 1024. Você pode ajustar isso modificando:

```python
portas_monitorar = range(1, 1025)
```

---

## 📂 Log de eventos

Os eventos são registrados no arquivo `monitor_portas.log`, indicando horário e quais portas foram abertas ou fechadas.

---

## 🤝 Sobre

Projeto feito para fins educacionais e aprendizado prático em Python e Cibersegurança, utilizando sockets, multithreading, requisições HTTP e integração com o Telegram.
