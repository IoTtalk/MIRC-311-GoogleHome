from voicetalk import cli


def application(*args, **kwargs):
    app = cli.main()

    return app(*args, **kwargs)
