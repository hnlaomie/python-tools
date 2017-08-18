import multiprocessing
import socket
from util.ctr.dsp.dsp_predict import OnlineService


def handle(connection, address):
    import logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger("process-%r" % (address,))
    try:
        logger.debug("Connected %r at %r", connection, address)
        while True:
            data = connection.recv(1024)
            if data == b'':
                logger.debug("Socket closed remotely")
                break
            predict_service = OnlineService.getInstance()
            predict = predict_service.predict(str(data))
            # logger.debug("Received data %r", data)
            connection.sendall(str(predict).encode())
            # logger.debug("Sent data")
    except:
        logger.exception("Problem handling request")
        connection.sendall(str(-1).encode())
    finally:
        logger.debug("Closing socket")
        connection.close()


class Server(object):
    def __init__(self, hostname, port):
        import logging
        self.logger = logging.getLogger("server")
        self.hostname = hostname
        self.port = port

    def start(self):
        self.logger.debug("listening")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.hostname, self.port))
        self.socket.listen(1)

        while True:
            conn, address = self.socket.accept()
            self.logger.debug("Got connection")
            process = multiprocessing.Process(target=handle, args=(conn, address))
            process.daemon = True
            process.start()
            self.logger.debug("Started process %r", process)


if __name__ == "__main__":
    predict_service = OnlineService.getInstance()
    print('begin load weights')
    predict_service.load_w('/home/laomie/projects/python/data/dsp_model.csv')
    predict_service.load_learner(.1, .4, .08)
    print('end load weights')

    import logging
    logging.basicConfig(level=logging.DEBUG)
    server = Server("localhost", 50051)
    try:
        logging.info("Listening")
        server.start()
    except:
        logging.exception("Unexpected exception")
    finally:
        logging.info("Shutting down")
        for process in multiprocessing.active_children():
            logging.info("Shutting down process %r", process)
            process.terminate()
            process.join()
    logging.info("All done")
