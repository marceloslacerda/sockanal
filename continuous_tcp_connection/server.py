import concurrent.futures
import logging
import socket

import common


def client_thread(conn, addr):
    with conn:
        while True:
            logging.debug(f"Receiving data from {addr}")
            try:
                data = common.receive_message(conn)
            except ConnectionResetError:
                logging.exception("Connection reset by peer")
                return
            if not data:
                logging.error(f"{addr} closed before sending a message")
                return
            elif len(data) != common.PAYLOAD_LENGTH:
                logging.error(f"{addr} sent an incomplete payload {data}")
            else:
                common.parse_msg_to_timestamp(addr, data)
            logging.debug(f"Sending reply to {addr}")
            common.send_timestamp(conn, addr)
    

def run_server():
    logging.info("Starting in server mode")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        logging.info(f"Binding to port {common.PORT}")
        s.bind((common.HOST, common.PORT))
        logging.info("Listening for incoming connections")
        s.listen(common.MAX_CONN)
        futures = [None] * common.MAX_CONN
        with concurrent.futures.ThreadPoolExecutor(max_workers=common.MAX_CONN) as executor:
            while True:
                # Continuously accept connections
                conn, addr = s.accept()
                logging.debug(f'Connected by {addr}')
                idx = -1
                while True:
                    # Iter over each worker untill a free one can be found to handle the connection
                    idx += 1
                    prev_future = futures[idx]
                    if prev_future is None or prev_future.done():
                        # Worker slot is free, assign it the connection and break the loop
                        if prev_future and prev_future.exception():
                            logging.exception(prev_future.exception())
                        futures[idx] = executor.submit(client_thread, conn, addr)
                        break


if __name__ == "__main__":
    logging.basicConfig(level=common.LOGLEVEL, format='%(levelname)s %(asctime)s: %(message)s')
    run_server()
