from dataclasses import dataclass


@dataclass
class SigninReq:
    username: str
    password: str