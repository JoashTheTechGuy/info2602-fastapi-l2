from sqlmodel import Field, SQLModel
from typing import Optional
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    password: str

    def set_password(self, password: str) -> None:
        self.password = password_hash.hash(password)

    @classmethod
    def create(cls, username: str, email: str, password: str):
        user = cls(username=username, email=email, password="")
        user.set_password(password)
        return user

    def __str__(self) -> str:
        return f"(User id={self.id}, username={self.username}, email={self.email})"
