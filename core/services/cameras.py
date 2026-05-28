"""Mock de feeds de câmeras."""

from core.datetime_br import format_datetime_sec_br, localnow


def listar_cameras():
    agora = localnow()
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
            "timestamp": format_datetime_sec_br(agora),
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
            "timestamp": format_datetime_sec_br(agora),
        },
    ]
