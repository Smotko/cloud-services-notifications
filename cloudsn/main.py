#!/usr/bin/python

from core.controller import Controller


def main ():
    cr = Controller.get_instance()
    cr.start()

if __name__ == "__main__":
    main()


