import argparse

SUPPRESS = '==SUPPRESS=='
parser = argparse.ArgumentParser(prog='Test UI', description='A test continuous UI', add_help=False,
                                 exit_on_error=False)
parser.add_argument("-h", "--help", action='help', default=SUPPRESS, help= "show this help message")
parser.add_argument("-a", "--a", dest="a_flag", action="store_true", help="Option A")
parser.add_argument("-b", "--b", dest="b_flag", action="store_true", help="Option B")
parser.add_argument("-c", "--c", dest="c_flag", action="store_true", help="Option C")
parser.add_argument("-q", "--q", dest="q_flag", action="store_true", help="Option Q")

def main():
    while True:
        text = input(">> ")
        if len(text) == 0:
            text = "--help"
        if text[0] != "-":
            text = "-"+text
        try:
            args = parser.parse_args(text.lower().split())
            if args.a_flag:
                print("A")
            if args.b_flag:
                print("B")
            if args.c_flag:
                print("C")
            if args.q_flag:
                print("Quiting...")
                break
        except SystemExit as e:
            pass

if __name__ == "__main__":
    main()
    input("Press [ENTER] to quit:")