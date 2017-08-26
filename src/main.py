#!/usr/bin/env python3

from manager import Manager

from utils.formatter import formatter


if __name__ == '__main__':
    print(formatter('ReactRouter'))

    creator_manager = Manager()
    creator_manager.run()

