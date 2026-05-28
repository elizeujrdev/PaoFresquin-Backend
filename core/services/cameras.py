"""Mock de feeds de câmeras."""

from datetime import datetime


def listar_cameras():
    agora = datetime.now()
    return [
        {
            "id": "cam-01",
            "codigo": "CAM 01",
            "local": "LOJA",
            "titulo": "Loja — balcão e caixa",
            "qualidade": "1080p · 30fps",
            "online": True,
            "stream_url": None,
            "placeholder": "[ feed da câmera ]",
            "timestamp": agora.strftime("%d/%m/%Y %H:%M:%S"),
        },
        {
            "id": "cam-02",
            "codigo": "CAM 02",
            "local": "COZINHA",
            "titulo": "Cozinha — forno e bancada",
            "qualidade": "1080p · 30fps",
            "online": True,
            "stream_url": None,
            "placeholder": "[ feed da câmera ]",
            "timestamp": agora.strftime("%d/%m/%Y %H:%M:%S"),
        },
    ]
