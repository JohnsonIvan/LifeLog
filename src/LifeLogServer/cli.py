import argparse
import LifeLogServer
from flask import Flask

def main():
    parser = argparse.ArgumentParser(
        description=f"Hello World!\nVersion: {LifeLogServer.API_VERSION}",
    )

    args = parser.parse_args()

    app = LifeLogServer.create_app()
    app.run(host="0.0.0.0", port=5000)


if __name__ == "__main__":
    main()
