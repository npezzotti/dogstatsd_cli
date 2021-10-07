from tests.common import INVALID_TAGS
import pytest
from dogstatsd_cli.dogstatsd import DogstatsdClient


def test_default_host_port(dogstatsd_client_default_instance):
    client = dogstatsd_client_default_instance
    assert client.host == 'localhost'
    assert client.port == 8125


def test_default_sample_rate():
    client = DogstatsdClient(default_sample_rate=.5)
    assert client.default_sample_rate == .5


def test_socket_path():
    client = DogstatsdClient(socket_path='/test/socket')
    assert client.socket_path == '/test/socket'


def test_socket_path_precedence():
    client = DogstatsdClient(host='test', port=8000, socket_path='/test/socket')
    assert not client.host and not client.port



def test_normalize_tags(dogstatsd_client_default_instance):

    normalized_tags = list(tag for tag in dogstatsd_client_default_instance.normalize_tags((INVALID_TAGS)))
    print(normalized_tags)

    assert normalized_tags == ['test:tag', '_est:tag', 't_st:tag', 'te_t:tag', 'tes_:tag', 'test:_ag', 'test:t_g', 'test:ta_' 'test:_tag']