from core.cleanup import graceful_exit

def sinput(prompt):
    try:
        return input(prompt)
    except EOFError:
        return graceful_exit()

