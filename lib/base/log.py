"""Logging module."""

import logging
import yaml

def logger(testCase, device='MAIN'):
    """Retrieve Python logger."""
    log = logging.getLogger(testCase)
    if not len(log.handlers):
        log.setLevel(logging.DEBUG)
        log_format = ' '.join(['%(asctime)s', ':', '[%(levelname)s]',
                               '[%(name)s]', '[%(device)s]',
                               '[%(funcName)s]', '%(message)s'])
        log_formatter = logging.Formatter(log_format)
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)
        stream_handler.setFormatter(log_formatter)
        log.addHandler(stream_handler)
        # file_handler = logging.FileHandler(log_dirpath, 'w')
        # file_handler.setLevel(logging.DEBUG)
        # file_handler.setFormatter(log_formatter)
        # log.addHandler(file_handler)
    return logging.LoggerAdapter(log, {'device': device})

def test(testCase, device):
    log = logger(testCase, device)
    log.info('Failed to select %s.', 'ccc')
    log.warning('Failed to select %s.', 'ccc')

if __name__ == '__main__':
    test('test case', 'device')
