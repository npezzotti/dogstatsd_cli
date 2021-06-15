import socket
import os
import re
import time


DEFAULT_HOST='localhost'
DEFAULT_PORT=8126

INVALID_TAG_CHARACTERS=r'[^\w\d_\-:.\/]'

METRIC_TYPES=['increment', 'decrement', 'count', 'gauge', 'set', 'histogram', 'timed', 'distribution']

class DogstatsdClient():

    OK, WARNING, CRITICAL, UNKNOWN = (0, 1, 2, 3)

    def __init__(
        self,
        host=DEFAULT_HOST,
        port=DEFAULT_PORT,
        socket_path=None,
        ):

        if socket_path is not None:
            self.socket_path = socket_path
            self.host = None
            self.port = None
        else:
            self.socket_path = None
            self.host = host
            self.port = port

        self.encoding = "utf-8"
        self.socket = None

        self.namespace = os.environ.get('DD_NAMESPACE')
        self.constant_tags = os.environ.get('DD_TAGS')


    def send_packet(self, packet):
        print(packet)
        try:
            socket = self.get_socket()
            socket.send(packet.encode(self.encoding))
        except Exception as e:
            print("Unexpected error: %s", e)
        finally:
            self.close_socket()


    def get_socket(self):
        if not self.socket:
            if self.socket_path is not None:
                self.socket = self._get_uds_socket(self.socket_path)
            else:
                self.socket = self._get_udp_socket(self.host, self.port)
        
        return self.socket


    def close_socket(self):
        if self.socket:
            try:
                self.socket.close()
            except OSError as e:
                print("Unexpected error: %s", str(e))
            
            self.socket = None


    @staticmethod
    def _get_udp_socket(host, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect((host, port))
        return sock


    @staticmethod
    def _get_uds_socket(socket_path):
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        sock.connect(socket_path)
        return sock


    def _format_metric(self, metric, value, metric_type, sample_rate=None, tags=None):
        return '%s%s:%s|%s%s%s' % (
            (self.namespace + '.') if self.namespace else '',
            metric,
            value,
            metric_type,
            ('|@' + str(sample_rate)) if sample_rate else '',
            ('|#' + ','.join(self.normalize_tags(tags))) if tags else ''
        )

    @staticmethod
    def normalize_tags(tags):
        split_tags = set((tag for tag in tags.split(",") if tag))

        return (re.sub(INVALID_TAG_CHARACTERS, '_', tag.strip()) for tag in split_tags)


    def metric(self, mname, value, mtype, sample_rate=None, tags=None):
        message = self._format_metric(mname, value, mtype, sample_rate, tags)
        
        self.send_packet(message)
    
    def service_check(self, name, status, date=None, hostname=None, tags=None, message=None):
        if date is None:
            date=time.time()

        message = '_sc|%s%s|%s%s%s%s%s' % (
            (self.namespace + ".") if self.namespace else '',
            name,
            status,
            '|d:' + str(date),
            '|h:' + hostname if hostname else '',
            ('|#' + ','.join(self.normalize_tags(tags))) if tags else '',
            '|m:' + message if message else ''
        )
        
        self.send_packet(message)
    
    def event(
        self, 
        title, 
        text, 
        date=None, 
        hostname=None, 
        aggregation_key=None,
        priority=None, 
        source_type_name=None,
        alert_type=None, 
        tags=None
    ):

        if date is None:
            date=time.time()
        
        message = '_e{%d,%d}:%s|%s%s%s%s%s%s' % (
            len(title),
            len(text),
            title,
            text,
            '|d:{' + str(date),
            '|h:' + hostname if hostname else '',
            '|p:' + priority if priority else '',
            '|t:' + alert_type if alert_type else '',
            ('|#' + ','.join(self.normalize_tags(tags))) if tags else ''
        )
        
        self.send_packet(message)
