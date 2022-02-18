import sys
from collections import defaultdict as d


class Pizza:
    def __init__(self, taken=0, _likes=(), _dislikes=(), _idx=-1):
        self.taken = taken
        self.likes = _likes or set(likes)
        self.dislikes = _dislikes or set(dislikes)
        self.idx = _idx
        self.enemies = set([])
        self.comrades = set([])
        self.comrade_score = []
        self.comrades_sorted = []
        self.parent = -1


def add(_idx, parent=-1):
    global taken_idxes, not_taken_idxes, taken_freq
    taken_idxes |= {_idx}
    not_taken_idxes -= {_idx}
    _pizza = pizzas[_idx]
    for _like in _pizza.likes:
        taken_freq[_like] += 1
    _pizza.taken = 1
    _pizza.parent = parent


def remove(_idx):
    global taken_idxes, not_taken_idxes, taken_freq
    taken_idxes -= {_idx}
    not_taken_idxes |= {_idx}
    _pizza = pizzas[_idx]
    for _like in _pizza.likes:
        taken_freq[_like] -= 1
    _pizza.taken = 0


def safe_add(_idx, del_max, parent=-1):
    if net_addition([_idx]) >= 1 - del_max:
        add(_idx, parent)
        enemies = pizzas[_idx].enemies & taken_idxes
        if enemies:
            print >> sys.stderr, -len(enemies)
            [remove(i) for i in enemies]
        return True
    return False


def net_addition(idxes):
    addition = 0
    prospective_taken_idxes = set([])
    for _idx in idxes:
        _pizza = pizzas[_idx]
        clashes = len(_pizza.enemies & (prospective_taken_idxes | taken_idxes))
        addition += 1 - clashes
        prospective_taken_idxes |= {_idx}
    return addition


def get_difference_index(idxes):
    # How different pizza_2 is from pizza_1 (base-line). Lower means more similar
    diff_idx = 0
    for i in range(len(idxes)-1):
        pizza_1 = pizzas[idxes[i]]
        for j in range(i+1, len(idxes)):
            pizza_2 = pizzas[idxes[j]]
            diff_idx -= len(pizza_1.likes & pizza_2.likes) * 2
            diff_idx -= len(pizza_1.dislikes & pizza_2.dislikes) * 2
            diff_idx += len(pizza_2.likes - pizza_1.likes)
            diff_idx += len(pizza_2.dislikes - pizza_1.dislikes)
    return diff_idx


def get_available_comrades(_idx, amt):
    comrades = pizzas[_idx].comrades_sorted
    available = []
    for comrade in comrades:
        if len(available) == amt:
            break
        if comrade in not_taken_idxes:
            available.append(comrade)
    return available


def get_next():
    # order = sorted(not_taken_idxes, key=lambda _idx: (get_not_taken_displaced_ct(_idx),
    #                                                  get_difference_index(get_available_comrades(_idx, size-1)),
    #                                                  net_addition(get_available_comrades(_idx, size-1))))
    order = sorted(not_taken_idxes, key=sort_fn)
    if not order:
        return []
    _pizza = pizzas[order[0]]
    return [_pizza.idx] + get_available_comrades(_pizza.idx, size-1)


def final_score():
    final = set(taken_ingredients())
    ok = 0
    for idx in range(n):
        good = 1
        pizza = pizzas[idx]
        for like in pizza.likes:
            good &= (like in final)
        for dislike in pizza.dislikes:
            good &= (dislike not in final)
        ok += good
    return ok


sort_fn = lambda _idx: (get_taken_displaced_ct(_idx), get_not_taken_displaced_ct(_idx))
sort_fn_2 = lambda _idx: (get_not_taken_displaced_ct(_idx),
                          get_difference_index(get_available_comrades(_idx, size-1)),
                          net_addition(get_available_comrades(_idx, size-1)))


def re_init(_sort_fn=sort_fn):
    global taken_idxes, not_taken_idxes, taken_freq, sort_fn
    taken_idxes = set([])
    not_taken_idxes = set(range(n))
    taken_freq = d(int)
    for pizza in pizzas:
        pizza.parent = -1
    sort_fn = _sort_fn


def solve(_size, del_max):
    global size
    size = _size
    added, parent = True, -2
    while added:
        next_idxes = get_next()
        if not next_idxes:
            break
        for idx in next_idxes:
            if pizzas[idx].parent == parent:
                print >> sys.stderr, "encountered loop"
                added = False
                break
            added = safe_add(idx, del_max, parent)
            parent = len(not_taken_idxes)
            if not added:
                break
        print >> sys.stderr, len(not_taken_idxes)

    final_pizza = taken_ingredients()
    out = open("fme.txt", "w")
    print >> out, len(final_pizza), " ".join(sorted(final_pizza))
    print >> sys.stderr, "score =", final_score()


ingredients_like_idx = d(set)
ingredients_dislike_idx = d(set)
pizzas = []
taken_idxes = set([])
taken_freq = d(int)
taken_ingredients = lambda: [ingr for ingr in taken_freq if taken_freq[ingr]]
get_taken_displaced_ct = lambda _idx: len(pizzas[_idx].enemies & taken_idxes)
get_not_taken_displaced_ct = lambda _idx: len(pizzas[_idx].enemies & not_taken_idxes)

sys.stdin = open("/Users/fortune/Downloads/input_data/d_difficult.in.txt")
n = input()
not_taken_idxes = set(range(n))
for idx in range(n):
    likes = set(raw_input().split()[1:])
    dislikes = set(raw_input().split()[1:])
    for like in likes:
        ingredients_like_idx[like] |= {idx}
    for dislike in dislikes:
        ingredients_dislike_idx[dislike] |= {idx}
    pizzas.append(Pizza(0, likes, dislikes, idx))

for pizza in pizzas:
    for like in pizza.likes:
        pizza.enemies |= ingredients_dislike_idx[like]
    for dislike in pizza.dislikes:
        pizza.enemies |= ingredients_like_idx[dislike]
    pizza.comrades = set(range(n)) - (pizza.enemies | {pizza.idx})  # any reason this is a set? score sorted list?
    for comrade_idx in pizza.comrades:
        pizza.comrade_score.append(get_difference_index([pizza.idx, comrade_idx]))
    pizza.comrades_sorted = [x[1] for x in sorted(zip(pizza.comrade_score, pizza.comrades))]

sys.stdin = open("/dev/tty")
solve(1, 0)
# to re-run
# re_init(_sort_fn=sort_fn)
# solve(1, 0)