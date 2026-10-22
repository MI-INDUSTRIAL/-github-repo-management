from datetime import datetime

def log_action(action, repository, status):

    with open("audit.log", "a") as file:
        file.write(
            f"{datetime.utcnow()},"
            f"{action},"
            f"{repository},"
            f"{status}\n"
        )
