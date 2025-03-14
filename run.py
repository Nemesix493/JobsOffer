import os

if __name__ == "__main__":
    os.environ.setdefault(
        'SETTINGS_MODULE',
        'settings'
    )
    from list_jobs_tech.commands.main_command import MainCommand
    MainCommand.run()
