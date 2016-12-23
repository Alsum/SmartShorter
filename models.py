from mongoframes import *


class Shortlink(Frame):
    # The fields each document in our collection will store
    _fields = {
        'slug',
        'ios',
        'android',
        'web'
    }

class Ios(SubFrame):

    _fields = {
        'primary',
        'fallback'
        }

class Android(SubFrame):

    _fields = {
        'primary',
        'fallback'
        }
