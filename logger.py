
path = 'new.log'

def logger(func):
    def wrapped(*args, **kwargs):
        with open(path, 'a') as f:
            r = func(*args, **kwargs)
            f.write('function {} return {}'.format(func.__name__, r)+'\n')
            return r
    return wrapped