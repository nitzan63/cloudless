import ray

ray.init(address="ray://34.134.59.39:10001")

@ray.remote
def compute_square(x):
    import time
    time.sleep(1)
    return f'{x} squared is {x * x}'

results = ray.get([compute_square.remote(x) for x in range(10)])

print(results) 