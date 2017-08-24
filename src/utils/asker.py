def ask(text='***', validate=lambda: True, mutate=lambda res: res):
    while True:
        res = input(text)
        if validate(res):
            return mutate(res)
