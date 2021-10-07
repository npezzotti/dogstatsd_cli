import socket
import os
import re
from time import time
from logging import getLogger

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 8125

INVALID_TAG_CHARACTERS=r'[^\w\d_\-:.\/]'

SERVICE_CHECK_STATUSES = [str(n) for n in range(4)]

class DogstatsdClient():

    def __init__(
        self,
        host=DEFAULT_HOST,
        port=DEFAULT_PORT,
        socket_path=None,
        default_sample_rate=1
        ):
        
        self.logger = getLogger('dogstatsd-cli')

        self.host = host
        self.port = port
        self.socket_path = socket_path

        if socket_path is not None:
            self.socket = socket_path
            self.host = None
            self.port = None
            self.logger.debug('* Using UDS...')

        self.encoding = "utf-8"
        
        self.socket = None

        self.namespace = os.environ.get('DD_NAMESPACE')

        if self.namespace:
            self.logger.debug('* Found DD_NAMESPACE, using namespace %s' % self.namespace)

        self.constant_tags = tuple(tag for tag in os.environ.get('DD_TAGS', '').split(',') if tag)
        
        for tag in self.constant_tags:
            self.logger.debug('* Sourced %s from DD_TAGS' % tag)
        
        self.default_sample_rate = default_sample_rate


    def send_packet(self, packet):
        try:
            sock = self.get_socket()
            sock.send(packet.encode(self.encoding))
            self.logger.info('* Packet sent: %s' % packet)
        except OSError as e:
            self.logger.error('Error: %s\nUse --verbose flag for more details', e)
        finally:
            self.close_socket()
            self.logger.debug('* Connection closed.')


    def get_socket(self):
        if not self.socket:
            if self.socket_path is not None:
                self.logger.debug('* Connecting to UDS socket %s...' % self.socket_path)
                self.socket = self._get_uds_socket(self.socket_path)
            else:
                self.logger.debug('* Connecting to %s:%s...' % (self.host, self.port))
                self.socket = self._get_udp_socket(self.host, self.port)
        
        return self.socket


    def close_socket(self):
        if self.socket:
            try:
                self.logger.debug('* Closing connection...')
                self.socket.close()
            except OSError as e:
                self.logger.error("Error: %s\nUse --verbose flag for more details's", e)
            
            self.socket = None


    @staticmethod
    def _get_udp_socket(host, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setblocking (False)
        sock.connect((host, port))
        return sock


    @staticmethod
    def _get_uds_socket(socket_path):
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        sock.setblocking(False)
        sock.connect(socket_path)
        return sock


    def _format_metric(self, metric, value, metric_type, sample_rate, tags=None):
        tags += self.constant_tags
        
        if sample_rate is None or sample_rate >= 1:
            sample_rate = self.default_sample_rate

        return '%s%s:%s|%s%s%s' % (
            (self.namespace + '.') if self.namespace else '',
            metric,
            value,
            metric_type,
            '|@' + str(sample_rate),
            ('|#' + ','.join(self.normalize_tags(tags))) if tags else ''
        )


    @staticmethod
    def normalize_tags(tags):
        return (re.sub(INVALID_TAG_CHARACTERS, '_', tag.strip()) for tag in tags)


    def increment(self, name, value=1, sample_rate=None, tags=None):
        message = self._format_metric(name, value, 'c', sample_rate, tags)

        self.send_packet(message)


    def decrement(self, name, value=1, sample_rate=None, tags=None):
        message = self._format_metric(name, -abs(value), 'c', sample_rate, tags)

        self.send_packet(message)
        

    def count(self, name, value, sample_rate=None, tags=None):
        message = self._format_metric(name, value, 'c', sample_rate, tags)

        self.send_packet(message)


    def gauge(self, name, value, sample_rate=None, tags=None):
        message = self._format_metric(name, value, 'g', sample_rate, tags)
        
        self.send_packet(message)


    def set(self, name, value, sample_rate=None, tags=None):
        message = self._format_metric(name, value, 's', sample_rate, tags)
        
        self.send_packet(message)


    def histogram(self, name, value, sample_rate=None, tags=None):
        message = self._format_metric(name, value, 'h', sample_rate, tags)
        
        self.send_packet(message)


    def timer(self, name, value, sample_rate=None, tags=None):
        message = self._format_metric(name, value, 'ms', sample_rate, tags)
        
        self.send_packet(message)


    def distribution(self, name, value, sample_rate, tags=None):
        message = self._format_metric(name, value, 'd', sample_rate, tags)
        
        self.send_packet(message)


    def service_check(self, name, status, date=None, hostname=None, tags=None, message=None):
        if status not in SERVICE_CHECK_STATUSES:
            self.logger.error("Invalid status: must be one of '0', '1', '2', '3'")
            return

        tags += self.constant_tags

        if date is None:
            date=time()

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
        tags += self.constant_tags

        if date is None:
            date=time()
        
        message = '_e{%d,%d}:%s|%s%s%s%s%s%s%s%s' % (
            len(title),
            len(text),
            title,
            text,
            '|d:' + str(date),
            '|h:' + hostname if hostname else '',
            '|k:' + aggregation_key if aggregation_key else '',
            '|p:' + priority if priority else '',
            '|s:' + source_type_name if source_type_name else '',
            '|t:' + alert_type if alert_type else '',
            ('|#' + ','.join(self.normalize_tags(tags))) if tags else ''
        )
        
        self.send_packet(message)
