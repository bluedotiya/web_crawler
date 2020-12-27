import subprocess
from multiprocessing import Pool
import os


class Validator:
    def __init__(self, result_path, tmp_path):
        self.result_path = result_path
        self.tmp_path = tmp_path
        self.deduped_list = []
        self.duped_list = []
        self.valid_list = []

    def dedupe(self):
        self.deduped_list = set(self.duped_list)

    def read_file(self):
        with open(self.tmp_path, "r") as tmp_file:
            self.duped_list = tmp_file.readlines()

    def validate(self):
        with Pool(40) as pool:
            self.valid_list = pool_filter(pool, ping_check, self.deduped_list)

    def write_file(self):
        with open(self.result_path, "a") as result_file:
            result_file.writelines(self.valid_list)

    def remove_tmp(self):
        os.remove(self.tmp_path)


def ping_check(url_str):
    if "http://" in url_str:
        hostname = url_str[7:-1]
    else:
        hostname = url_str[8:-1]
    if os.name == 'nt':
        count_char = '-n'
    else:
        count_char = '-c'
    status = subprocess.call(
        ['ping', count_char, '1', hostname], stdout=open(os.devnull, 'wb'))
    if status == 0:
        return True
    else:
        return False


def pool_filter(pool, func, candidates):
    return [c for c, keep in zip(candidates, pool.map(func, candidates)) if keep]
