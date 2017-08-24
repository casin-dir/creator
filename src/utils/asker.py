def ask(text='***', validate=lambda res: True, mutate=lambda res: res):
    while True:
        res = input(text)
        if validate(res):
            return mutate(res)
