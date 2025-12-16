import os

from dotenv import load_dotenv


def load_env_vars(func):

    def wrapper(*args, **kwargs):
        if os.path.exists(".env"):
            load_dotenv(".env", override=True)
        return func(*args, **kwargs)

    return wrapper
