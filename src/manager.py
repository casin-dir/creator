import sys
import getopt

from generator import Generator


class Manager:
    def __init__(self):
        self.target_path = None
        self.target_name = None
        self.template_path = None
        self.generator = None

    def run(self):
        optlist, args = getopt.getopt(sys.argv[1:], 'p:t:', ['path=', 'template='])
        for opt, arg in optlist:
            if opt in ('-p', '--path'):
                self.target_path = arg
            elif opt in ('-t', '--template'):
                self.template_path = arg
            else:
                sys.exit(1)
        self.target_name = args[0]
        self.generate()

    def generate(self):
        self.generator = Generator(self.template_path, self.target_path, self.target_name)
        self.generator.run()



