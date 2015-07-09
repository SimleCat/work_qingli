#! /usr/bin/python
# -*- coding: utf-8

import sys
import time

STYLE = {
        'fore': {
                'black': 30, 'red': 31, 'green': 32, 'yellow': 33,
                'blue': 34, 'purple': 35, 'cyan': 36, 'white': 37,
        },
        'back': {
                'black': 40, 'red': 41, 'green': 42, 'yellow': 43,
                'blue': 44, 'purple': 45, 'cyan': 46, 'white': 47,
        },
        'mode': {
                'bold': 1, 'underline': 4, 'blink': 5, 'invert': 7,
        },
        'default': {
                'end': 0,
        }
}
 
def useStyle(string, mode='', fore='', back=''):
    mode = '%s' % STYLE['mode'][mode] if STYLE['mode'].has_key(mode) else ''
    fore = '%s' % STYLE['fore'][fore] if STYLE['fore'].has_key(fore) else ''
    back = '%s' % STYLE['back'][back] if STYLE['back'].has_key(back) else ''
    style = ';'.join([s for s in [mode, fore, back] if s])
    style = '\033[%sm' % style if style else ''
    end = '\033[%sm' % STYLE['default']['end'] if style else ''

    return '%s%s%s' % (style, string, end)

def getTerminalSize():
    import os
    env = os.environ
    def ioctl_GWINSZ(fd):
        try:
            import fcntl, termios, struct, os
            cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ,
        '1234'))
        except:
            return
        return cr
    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        cr = (env.get('LINES', 25), env.get('COLUMNS', 80))

    return int(cr[1]), int(cr[0])

terminal_width, terminal_hight = getTerminalSize()

def updateTerminalSize():
    global terminal_width
    global terminal_hight
    terminal_width, terminal_hight = getTerminalSize()

# 清除屏幕
def clearScreen():
    sys.stdout.write("\033[2J")

# 清除从光标到行尾的内容
def clearLine():
    sys.stdout.write("\033[K")

# 光标复位
def resetCursor():
    sys.stdout.write("\033[H")

# 光标保存
def saveCursor():
    sys.stdout.write("\033[s")

# 光标恢复  
def recoverCursor():
    sys.stdout.write("\033[u")

# 光标隐藏
def hideCursor():
    sys.stdout.write("\033[?25l")

# 光标显示
def showCursor():
    sys.stdout.write("\033[?25h")

# 定位光标
def moveCursor(x, y):
    sys.stdout.write("\033[%d;%dH" % (y, x))

# 上移光标
def moveupCursor(y):
    sys.stdout.write("\033[%dA" % y)

# 下移光标
def movedownCursor(y):
    sys.stdout.write("\033[%dB" % y)

# 左移光标
def moveleftCursor(x):
    sys.stdout.write("\033[%dD" % x)

# 右移光标
def moverightCursor(x):
    sys.stdout.write("\033[%dC" % x)


def printString(x, y, string, mode='', fore='', back=''):
    moveCursor(x, y)
    str_style = useStyle(string, mode, fore, back)
    sys.stdout.write(str_style)
    sys.stdout.flush()

def printString_Center(num_line, string, mode='', fore='', back=''):
    moveCursor(1, num_line)
    length = len(string)
    x = terminal_width//2 - length//2 + 1
    # printString(x, 2, "x = %d, num_line = %d" % (x, num_line))
    printString(x, num_line, string, mode, fore, back)



def printHLine(x, y, length, ch, mode='', fore='', back=''):
    printString(x, y, ch*length, mode, fore, back)

def printVLine(x, y, hight, ch, mode='', fore='', back=''):
    for i in range(hight):
        printString(x, y+i, ch, mode, fore, back)

def printRectangle(x1, y1, x2, y2, ch, mode='', fore='', back=''):
    printHLine(x1, y1, x2-x1+1, ch, mode, fore, back)
    printVLine(x1, y1+1, y2-y1, ch, mode, fore, back)
    printHLine(x1, y2, x2-x1+1, ch, mode, fore, back)
    printVLine(x2, y1+1, y2-y1, ch, mode, fore, back)

def printSolidRectangle(x1, y1, x2, y2, ch, mode='', fore='', back=''):
    width = x2-x1+1
    for y in range(y1, y2+1):
        printHLine(x1, y, width, ch, mode, fore, back)

def printRectangle_Amend(x1, y1, x2, y2, ch, mode='', fore='', back=''):
    printHLine(x1, y1, x2-x1+1, ch, mode, fore, back)
    printVLine(x1, y1+1, y2-y1, ch, mode, fore, back)
    printVLine(x1+1, y1+1, y2-y1, ch, mode, fore, back)
    printHLine(x1, y2, x2-x1+1, ch, mode, fore, back)
    printVLine(x2-1, y1+1, y2-y1, ch, mode, fore, back)    
    printVLine(x2, y1+1, y2-y1, ch, mode, fore, back)

 
class OverScolling(object):
    def __init__(self, x1, y1, x2, y2, mode='', fore='', back=''):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.mode = mode
        self.fore = fore
        self.back = back
        self.width = x2 - x1 + 1
        self.hight = y2 - y1 + 1
        # self.cur_line = y1
        self.str_list = []
        self.str_list.append(('', 0))
        self.setCanvas()
        # print "width = %d, hight = %d" % (self.width, self.hight)

    def setCanvas(self):
        printSolidRectangle(self.x1, self.y1, self.x2, self.y2, ' ', \
            self.mode, self.fore, self.back)

    def __addString_base(self, string):
        self.str_list.append((string, len(string)))
        if len(self.str_list) - 1 > self.hight:
            self.str_list = self.str_list[1:]
        for i in range(self.hight):
            if len(self.str_list) - 1 <= i:
                break
            diff = 0 if self.str_list[i][1] <= self.str_list[i+1][1] \
                        else self.str_list[i][1] - self.str_list[i+1][1]
            string = self.str_list[i+1][0] + ' ' * diff
            printString(self.x1, self.y1+i, string, self.mode, self.fore, self.back)
        moveCursor(self.x1+self.str_list[-1][1], self.y1+len(self.str_list)-1-1)
        sys.stdout.flush()

    @staticmethod
    def splitStringByLength(string, length):
        res = []
        num = len(string) // length
        for i in range(num):
            res.append(string[length*i:length*(i+1)])
        res.append(string[length*num:])
        return res


    def addString(self, string):
        strings = self.splitStringByLength(string, self.width)
        # print string
        # print strings
        for s in strings:
            self.__addString_base(s)


class OverScollingCenter(OverScolling):
    def __init__(self, num_line, width, hight, mode='', fore='', back=''):
        self.num_line = num_line
        self.width = width if terminal_width > width else terminal_width
        self.hight = hight if terminal_hight > hight else terminal_hight
        self.mode = mode
        self.fore = fore
        self.back = back
        self.x1 = terminal_width//2 - self.width//2 + 1
        self.x2 = self.x1 + self.width - 1
        self.y1 = self.num_line
        self.y2 = self.y1 + self.hight - 1
        super(OverScollingCenter, self).__init__(self.x1, self.y1, self.x2, self.y2, \
            self.mode, self.fore, self.back)

def test():
    clearScreen()
    moveCursor(1, 1)
    printString_Center(1, "Scolling Test")
    # printRectangle(2, 2, 20, 10, ' ', mode='blink', fore='white', back='white')
    # printSolidRectangle(2, 10, 20, 20, ' ', mode='blink', fore='white', back='white')
    # print getTerminalSize()
    # scroll = OverScolling(2, 5, 50, 7, mode='', fore='green', back='black')
    scroll = OverScollingCenter(3, terminal_width-10, 15, mode='', fore='red', back='white')
    scroll1 = OverScolling(3, 21, terminal_width//2-2, 30, mode='bold', fore='whilte', back='green')
    scroll2 = OverScolling(terminal_width//2+2, 21, terminal_width-2, 30, mode='underline', fore='whilte', back='green')
    import time
    import random
    import sys
    cur_f = open(sys.argv[0], 'r')
    for i in range(100):
        # string = '#' * random.randint(0, 100) + '[%d]' % (i+1)
        string = repr(cur_f.readline())
        string1 = '$' * random.randint(0, 100) + '[%d]' % (i+1)
        string2 = '%' * random.randint(0, 100) + '[%d]' % (i+1)
        scroll.addString(string)
        scroll1.addString(string1)
        scroll2.addString(string2)
        time.sleep(0.5)
    cur_f.close()
    moveCursor(1, terminal_hight)


    # print ''


if __name__ == '__main__':
    test()