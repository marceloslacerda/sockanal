import logging
import socket
import sys
import time

import common

SLEEP_INTERVAL = 0.5

def client_loop(sock, host):
    while True:
        common.send_timestamp(sock, host)
        logging.debug("Waiting for a reply")
        data = common.receive_message(sock)
        if not data:
            logging.error(f"{host} closed before sending a reply")
            break
        elif len(data) != common.PAYLOAD_LENGTH:
            logging.error(f"{host} sent an incomplete payload {data}")
        else:
            common.parse_msg_to_timestamp(host, data)
        time.sleep(SLEEP_INTERVAL)

def main():
    if len(sys.argv) > 1:
        host = sys.argv[1]
    else:
        host = common.HOST
    logging.info("Starting client program")
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                logging.info("Socket obtained")
                try:
                    sock.connect((host, common.PORT))
                except ConnectionRefusedError:
                    logging.error("Connection refused")
                    return
                logging.info(f"Connected to the server {host} on {common.PORT}")
                client_loop(sock, host)
        except BrokenPipeError:
            logging.error("Broken pipe")


if __name__ == "__main__":
    logging.basicConfig(level=common.LOGLEVEL, format='%(levelname)s %(asctime)s: %(message)s')
    main()