if True:  # pragma: no cover
    from flask import Flask

    import LifeLogServer
    import argparse
    import waitress


def start_init(subparser):  # pragma: no cover
    subparser.add_argument(
        "--database-file",
        default="/var/lib/lifelogserver/database.sqlite",
    )
    subparser.add_argument(
        "--config-file",
        default="/etc/lifelogserver/server.cfg",
    )
    subparser.add_argument("--port", default=5000, type=int)


def start_main(args):  # pragma: no cover
    app = LifeLogServer.create_app(
        config_file=args.config_file,
        database_file=args.database_file,
    )
    # TODO: is it better to use the os.exec(['flask', '--debug', ...]) instead?
    # ditto for waitress?
    if app.config["TESTING"]:
        app.run(host="0.0.0.0", port=args.port)
    else:
        waitress.serve(app, listen=f"*:{args.port}")


def main():  # pragma: no cover
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest="subcommand")
    subparsers.required = True

    commands = {
        "start": {
            "init": start_init,
            "main": start_main,
            "help": "Launch the lifelog server",
        },
    }

    for cmd_name in commands:
        cmd = commands[cmd_name]
        subparser = subparsers.add_parser(cmd_name, help=cmd["help"])
        cmd["init"](subparser)

    args = parser.parse_args()

    commands[args.subcommand]["main"](args)


if __name__ == "__main__":  # pragma: no cover
    main()
