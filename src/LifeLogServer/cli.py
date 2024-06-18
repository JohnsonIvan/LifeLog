# TODO: write tests for this entire file


import argparse  # pragma: no cover
import LifeLogServer  # pragma: no cover
from flask import Flask  # pragma: no cover


def main():  # pragma: no cover
    parser = argparse.ArgumentParser(
        description=f"Hello World!\nVersion: {LifeLogServer.API_VERSION}",
    )

    args = parser.parse_args()

    app = LifeLogServer.create_app()
    app.run(host="0.0.0.0", port=5000)


if __name__ == "__main__":  # pragma: no cover
    main()
