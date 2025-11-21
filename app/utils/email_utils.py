import requests


RESEND_API_KEY = ""

def enviar_mail_resend(destinatario, asunto, contenido_html):
    response = requests.post(
        "",
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "from": "Zoonosis Bariloche <notificaciones@sanidadanimalbariloche.com>",
            "to": [destinatario],
            "subject": asunto,
            "html": contenido_html
        }
    )
    return response.status_code, response.json()
