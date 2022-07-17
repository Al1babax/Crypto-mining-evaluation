def merge(l):
    if len(l) <= 1:
        return l
    mid = len(l)//2
    left = l[:mid]
    right = l[mid:]
    left = merge(left)
    right = merge(right)
    return compare_two_halves(left, right)


def compare_two_halves(left, right):
    res = []
    while len(left) != 0 and len(right) != 0:
        if left[0]['price2'] > right[0]['price2']:
            res.append(right[0])
            right.remove(right[0])
        else:
            res.append(left[0])
            left.remove(left[0])
    if len(right) == 0:
        res = res+left
    else:
        res = res+right
    return res
