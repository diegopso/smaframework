def _checkBackwards(needle, midpoint, alist, config):
    for i in range(midpoint-1, -1, -1):
        evaluated = config['key'](alist[i])
        if evaluated != needle:
            break
        midpoint = i

    return midpoint

def binarySearch(alist, needle, **kwargs):
    '''
     * Performs a binary search in a list.
     * 
     * @param   alist   The list to search.
     * @param   needle    The needle to search.
     * @return  int     The position of the closest needle.
    '''
    config = {
        'key': lambda element: element
    }
    config.update(kwargs)

    first = 0
    last = len(alist)-1

    while first <= last:
        if last == first:
            return first

        midpoint = (first + last)//2
        nextpoint = midpoint+1
        evaluated = config['key'](alist[midpoint])

        if evaluated == needle or needle > evaluated and needle < config['key'](alist[nextpoint]):
            return _checkBackwards(needle, midpoint, alist, config)
        else:
            if needle < evaluated:
                last = midpoint-1
            else:
                first = nextpoint

    return False
