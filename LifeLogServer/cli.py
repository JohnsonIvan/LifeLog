import argparse
import LifeLogServer

def main():
    parser = argparse.ArgumentParser(
        description=f"Hello World!\nVersion: {LifeLogServer.API_VERSION}",
    )
    parser.add_argument(
        "-m", "--message", default="Hello, World!", help="The message to print"
    )
    args = parser.parse_args()
    print(args.message)


if __name__ == "__main__":
    main()
