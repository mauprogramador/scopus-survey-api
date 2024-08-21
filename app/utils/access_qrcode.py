from io import StringIO
from socket import AF_INET, SOCK_DGRAM, socket

from qrcode.constants import ERROR_CORRECT_L
from qrcode.main import QRCode

from app.core.config.config import LOG


class ShowAccessQRCode:
    """Displays a QR code for mobile access"""

    __HOST = "10.253.155.219"
    __BASE_URL = "http://{ip}:{port}/scopus-searcher/api"
    __QR = QRCode(version=1, error_correction=ERROR_CORRECT_L)

    def __init__(self, port: int) -> None:
        """Displays a QR code for mobile access"""
        with socket(AF_INET, SOCK_DGRAM) as session:
            session.connect((self.__HOST, 58162))
            ip = str(session.getsockname()[0])

        url = self.__BASE_URL.format(ip=ip, port=port)
        self.__QR.add_data(url)
        self.__QR.make(fit=True)

        output_string = StringIO()
        self.__QR.print_ascii(out=output_string)
        output_string.seek(0)

        LOG.info("Scan the QR Code below to access via mobile:")
        print(output_string.read())
