import argparse
import sys


def main(argv):
    parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(
        prog='model-has-description',
    )
    parser.add_argument(
        "filenames",
        nargs="+",
    )
    args = parser.parse_args(argv)
    print(args.filenames)
    raise SystemExit(1)


if __name__ == "__main__":
    main(sys.argv)
