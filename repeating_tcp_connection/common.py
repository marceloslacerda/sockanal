import datetime
import logging
import os

logger = logging.getLogger(__name__)

PORT = int(os.environ.get("PORT", 7891))
HOST = os.environ.get("HOST", "localhost")
LOGLEVEL = os.environ.get("LOGLEVEL", "DEBUG").strip().upper()
EXAMPLE_DATE = datetime.datetime.now().isoformat()
PAYLOAD_LENGTH = len(EXAMPLE_DATE)
MAX_CONN = 5


def send_timestamp(conn, addr):
    logging.info("Sending message")
    msg = datetime.datetime.now().isoformat().encode("utf-8")
    totalsent = 0
    while totalsent < PAYLOAD_LENGTH:
        sent = conn.send(msg[totalsent:])
        if sent == 0:
            logging.error(f"{addr} closed before waiting reply")
            return
        totalsent = totalsent + sent


def receive_message(conn):
    chunks = []
    bytes_recd = 0
    while bytes_recd < PAYLOAD_LENGTH:
        chunk = conn.recv(min(PAYLOAD_LENGTH - bytes_recd, 2048))
        if chunk == b'':
            break
        chunks.append(chunk)
        bytes_recd = bytes_recd + len(chunk)
    return b''.join(chunks)


def parse_msg_to_timestamp(addr, data):
    try:
        data = data.decode()
        try:
            dt = datetime.datetime.fromisoformat(data)
            delta = datetime.datetime.now() - dt
            logging.info(f"Successfully received a message from {dt}, Delta: {delta.total_seconds()}")
        except ValueError:
            logging.error(f"{addr} sent {data} which is not a datetime")
    except UnicodeDecodeError:
        logging.error(f"{addr} sent {data} which is not utf-8")


