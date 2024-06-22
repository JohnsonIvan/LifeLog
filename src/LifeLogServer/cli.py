if True:  # pragma: no cover
    from flask import Flask

    import LifeLogServer
    import argparse
    import waitress
    import subprocess


def start_init(subparser):  # pragma: no cover
    subparser.add_argument(
        "--database-file",
        default=LifeLogServer.database.DEFAULT_DATABASE_LOCATION,
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


def db_shell_init(subparser):  # pragma: no cover
    subparser.add_argument(
        "--database-file",
        default=LifeLogServer.database.DEFAULT_DATABASE_LOCATION,
    )


def db_shell_main(args):  # pragma: no cover

    # TODO p:H: get automatic recompilation working; don't want to run
    # `nix-build` every single time

    # TODO actually get this working, then use it to debug failure in prod

    # TODO add support for passing in arbitrary arguments?
    # -> e.g. `lls db_shell "SELECT * FROM foo"`
    # -> (or not; echo 'SELECT * FROM foo' | lls db_shell` is just as effective?)
    subprocess.run(["sqlite3", args.database_file])


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
        "db-shell": {
            "init": db_shell_init,
            "main": db_shell_main,
            "help": "Open a shell for the database",
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
