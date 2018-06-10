
path = 'new.log'
y = (1,2,3,4,5,6)
def logger(func):
    def wrapped(*args, **kwargs):
        with open(path, 'a') as f:
            r = func(*args, **kwargs)
            f.write('function {} return {}'.format(func.__name__, r)+'\n')
            return r
    return wrapped

@logger
def square(x):
    return x**x


for x in y:
    square(x)