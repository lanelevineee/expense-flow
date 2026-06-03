import socket
from typing import Optional

try:
    import qrcode
    from qrcode.image.pil import PilImage
except ImportError:
    qrcode = None


def get_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def generate_qr_ascii(url: str, border: int = 1) -> str:
    if qrcode is None:
        return f"[QR code unavailable - install qrcode library]\nURL: {url}"

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=1,
        border=border,
    )
    qr.add_data(url)
    qr.make(fit=True)

    modules = qr.get_matrix()
    lines = []
    for row in modules:
        line = ""
        for cell in row:
            line += "\u2588\u2588" if cell else "  "
        lines.append(line)

    top = "\u2580" * (len(lines[0]))
    bottom = "\u2580" * (len(lines[0]))
    return f"{top}\n" + "\n".join(lines) + f"\n{bottom}"


def show_qr(port: int = 7070, path: str = "/", label: str = "") -> str:
    ip = get_local_ip()
    url = f"http://{ip}:{port}{path}"
    qr_art = generate_qr_ascii(url)
    title = label or "Scan to open Expense Tracker"
    return f"\n  {title}\n  {url}\n\n{qr_art}\n"
