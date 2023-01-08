import collections
import itertools
import multiprocessing
from multiprocessing import cpu_count
from timeit import default_timer
import logging

logging.basicConfig(level=logging.DEBUG, format='%(threadName)s %(message)s')


def get_prime_divisors(n):
    i = 2
    while i * i <= n:
        if n % i == 0:
            n /= i
            yield i
        else:
            i += 1

    if n > 1:
        yield n


def calc_product(iterable):
    acc = 1
    for i in iterable:
        acc *= i
    return acc


def get_all_divisors(n):
    primes = get_prime_divisors(n)

    primes_counted = collections.Counter(primes)

    divisors_exponentiated = [
        [div ** i for i in range(count + 1)]
        for div, count in primes_counted.items()
    ]

    for prime_exp_combination in itertools.product(*divisors_exponentiated):
        yield calc_product(prime_exp_combination)


def get_sorted_divisors(n):
    divisors_list = []
    for i in get_all_divisors(n):
        divisors_list.append(int(i))
    return sorted(divisors_list)


def execute_time(func):
    def delta_time(*args):
        t1 = default_timer()
        delta = default_timer() - t1
        logging.info(f'Run time {delta}')
        return func(*args)
    return delta_time


@execute_time
def factorize(*number):
    max_workers = cpu_count() * 2 + 1
    print("Pool started...")
    with multiprocessing.Pool(max_workers) as Pool:
        result = Pool.map(get_sorted_divisors, number)
    return result


if __name__ == '__main__':
    a, b, c, d = factorize(128, 255, 99999, 10651060)
    print(f'{a=}')
    print(f'{b=}')
    print(f'{c=}')
    print(f'{d=}')
    assert a == [1, 2, 4, 8, 16, 32, 64, 128]
    assert b == [1, 3, 5, 15, 17, 51, 85, 255]
    assert c == [1, 3, 9, 41, 123, 271, 369, 813, 2439, 11111, 33333, 99999]
    assert d == [1, 2, 4, 5, 7, 10, 14, 20, 28, 35, 70, 140, 76079, 152158, 304316, 380395, 532553, 760790, 1065106,
                 1521580, 2130212, 2662765, 5325530, 10651060]
