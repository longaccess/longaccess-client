import sys
from blessed import Terminal


def ask_key():
    t = Terminal()
    width = 64
    lwidth = 16
    movement = {
        'KEY_LEFT': -1,
        'KEY_RIGHT': 1,
        'KEY_UP': -lwidth,
        'KEY_DOWN': lwidth,
        'KEY_HOME': -width,
        'KEY_END': width,
        'KEY_BACKSPACE': -1
    }

    value = [" "] * width
    rows = ["B", "C", "D", "E"]

    def valid():
        return " " not in value

    with t.cbreak():
        val = None
        validvalue = None
        pos = 0
        nrows = width/lwidth
        print "Type the decryption key, or press 'q' to cancel"
        while val not in (u'q', u'Q',):
            for i in range(width/lwidth):
                s = lwidth / 2
                print rows[i],
                print t.underline("".join(value[2*i*s:(2*i+1)*s])),
                print t.underline("".join(value[(2*i+1)*s:(2*i+2)*s]))
            if valid():
                print "key valid, press enter to accept"
            else:
                print t.clear_eol
            if validvalue is not None:
                break
            sys.stdout.write(t.move_up * (nrows+1))
            with t.location():
                y = pos/lwidth
                x = pos % lwidth
                sys.stdout.write(t.move_down * y)
                sys.stdout.write(t.move_right * (x + 2 + (2*x)/lwidth))
                sys.stdout.flush()
                val = t.inkey(timeout=5)
                if not val:
                    pass
                elif val.is_sequence:
                    if val.name in movement:
                        newpos = pos + movement[val.name]
                        pos = min(width-1, max(0, newpos))
                    if val.name in ('KEY_DELETE', 'KEY_BACKSPACE'):
                        value[pos:width] = value[pos+1:width] + [" "]
                    elif val.name is 'KEY_ENTER' and valid():
                        validvalue = value
                elif val.lower() in "0123456789abcdef":
                    if pos < width:
                        value[pos] = val.upper()
                        if pos < width - 1:
                            pos += 1
    if validvalue is not None:
        return ("".join(validvalue)).decode('hex')
    return validvalue

if __name__ == "__main__":
    key = ask_key()
    if key is not None:
        print key.encode('hex')
