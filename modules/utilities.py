
def show_progress(i, n, width=10):
    b = int(width * i / n)
    l = int(width - b)
    print("\b"*width + u"\u2588"*b + "-"*l, end=None)
