import os
import socket
import sys
from celery import Celery


CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379'),
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379')
CELERY_CREATE_MISSING_QUEUES = True

celery = Celery('tasks', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND,
                task_create_missing_queues=CELERY_CREATE_MISSING_QUEUES)

@celery.task()
def printer(ip: str, message: str):
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening
    server_address = (ip, 9100)
    print(sys.stderr, 'connecting to %s port %s' % server_address)
    sock.connect(server_address)

    try:
        my_bytes = bytearray.fromhex(
            message)

        sock.sendall(my_bytes)

        # Look for the response
        amount_received = 0

        while amount_received <= 0:
            data = sock.recv(16)
            amount_received += len(data)
            print(sys.stderr, 'received "%s"' % data)
            print(sys.stderr, 'amount_received %d' % amount_received)
    except Exception as e:
        print('error', e)
    finally:
        print(sys.stderr, 'closing socket')
        sock.close()
        return "HELLO"
