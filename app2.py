import time
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import requests
import threading
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

app = Flask(__name__)
app.secret_key = 'xdw102392aK'

logs_sites_monitorados = []

# Lista separada para armazenar logs de erro do site
erro_logs_sites_monitorados = []

sites_logger = logging.getLogger('sites_logger')
sites_logger.setLevel(logging.INFO)
sites_handler = logging.FileHandler('sites_monitoring.log')
log_format = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
sites_handler.setFormatter(log_format)
sites_logger.addHandler(sites_handler)

sites_monitorados = []

def monitor_site(site):
    while True:
        try:
            response = requests.get(site['url'])
            if response.status_code != 200:
                enviar_email(site['email'], site['url'])
                log_message = f"Site {site['url']} está fora do ar"
                sites_logger.warning(log_message)
                logs_sites_monitorados.append(log_message)
                # Adicione o log de erro à lista de erros do site
                erro_logs_sites_monitorados.append(log_message)
            else:
                log_message = f"Site {site['url']} está acessível"
                sites_logger.info(log_message)
                logs_sites_monitorados.append(log_message)
        except Exception as e:
            log_message = f"Erro ao acessar {site['url']}: {str(e)}"
            sites_logger.error(log_message)
            logs_sites_monitorados.append(log_message)
            # Adicione o log de erro à lista de erros do site
            erro_logs_sites_monitorados.append(log_message)
        time.sleep(3600)

def enviar_email(destinatario, url):
    # Configurar suas informações de e-mail aqui
    remetente = 'myemailtest63@gmail.com'
    senha = 'L8l2l3l4@'

    msg = MIMEMultipart()
    msg['From'] = remetente
    msg['To'] = destinatario
    msg['Subject'] = 'Site fora do ar'

    corpo_email = f"O site {url} está fora do ar."
    msg.attach(MIMEText(corpo_email, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(remetente, senha)
        server.sendmail(remetente, destinatario, msg.as_string())
        server.quit()
    except Exception as e:
        print(f"Erro ao enviar e-mail: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html', sites=sites_monitorados)

@app.route('/adicionar', methods=['POST'])
def adicionar_site():
    url = request.form['url']
    email = request.form['email']
    
    site = {
        'url': url,
        'email': email
    }
    
    sites_monitorados.append(site)
    
    flash('Site adicionado com sucesso', 'success')
    
    monitor_thread = threading.Thread(target=monitor_site, args=(site,))
    monitor_thread.daemon = True
    monitor_thread.start()
    
    return redirect(url_for('index'))

@app.route('/logs')
def logs():
    logs_com_data_hora = [{'data_hora': time.strftime('%Y-%m-%dT%H:%M:%S'), 'mensagem': mensagem} for mensagem in erro_logs_sites_monitorados]
    return jsonify(logs_com_data_hora)

if __name__ == '__main__':
    app.run(debug=True)
