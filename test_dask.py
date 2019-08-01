from distributed import Client
from distributed.diagnostics import progress
import dask.bag as db

def square(x):
    return x * 3

def neg(x):
    return -x

c = Client('localhost:8786')
a = c.map(square, range(10))
b = c.map(neg, a)
total = c.submit(sum, b)
a = total.result()
print a


# b = db.from_url(['http1', 'http2'])
# df = b.to_dataframe()
# df.compute()
