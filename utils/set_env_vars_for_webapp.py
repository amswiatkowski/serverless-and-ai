#!/usr/bin/env python
# pylint: disable=wrong-import-position,import-error
import inspect
import os.path
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))), '../'))
from utils.cfn_reader import cfn_reader


def set_env_vars_for_webapp() -> str:
    return cfn_reader()['APIURL']


if __name__ == '__main__':
    print(set_env_vars_for_webapp())
