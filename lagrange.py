import math
import numpy as np

def build_w(xs,at) -> 'Our W func':
    def w(x) -> float:
        top = math.prod(x - xx for xx in xs if xx!=at)
        bot = math.prod(at - xx for xx in xs if xx!=at)
        return top/bot
    return w

def build_lagrange(xs, ys):
    def build_w(xs,at) -> 'Our W func':
        def w(x) -> float:
            top = math.prod(x - xx for xx in xs if xx!=at)
            bot = math.prod(at - xx for xx in xs if xx!=at)
            return top/bot
        return w
    def l(x) -> float:
        ws = [build_w(xs, at) for at in xs]
        combined = zip(ws, ys)
        final_list = [combo(x)*value for combo,value in combined]
        return sum(final_list)
    return l