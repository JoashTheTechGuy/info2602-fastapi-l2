import typer
from app.database import create_db_and_tables, get_session, drop_all
from app.models import User
from fastapi import Depends
from sqlmodel import select
from sqlalchemy.exc import IntegrityError

cli = typer.Typer()

@cli.command()
def initialize():
    """
    This command initializes the database
    """
    with get_session() as db: # Get a connection to the database
        drop_all() # delete all tables
        create_db_and_tables() #recreate all tables
        bob = User(
            username="bob",
            email="bob@mail.com",
            password="bobpass"
        )

        db.add(bob) # Tell the database about this new data
        db.commit() # Tell the database persist the data
        db.refresh(bob) # Update the user (we use this to get the ID from the db)
        print("Database Initialized")

@cli.command()
def get_user(username: str = typer.Argument(..., help="The username of the user you want to retrieve")):
    """
    This command returns a specified user
    """
    with get_session() as db: #get a connection to the database
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f'{username} not found!')
            return
        print (user)

@cli.command()
def get_all_users():
    """
    This command lists all users in the database
    """
    with get_session() as db:
        all_users = db.exec(select(User)).all()
        if not all_users:
            print("No users found")
        else:
            for user in all_users:
                print(user)


@cli.command()
def change_email(
    username: str = typer.Argument(..., help="The username of the user whose email you want to change"),
    new_email: str = typer.Argument(..., help="The new email address to set for the user")
):
    """
    Change the email of an existing user.

    This command finds a user by their username and updates their email address.
    """
    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f'{username} not found! Unable to update email.')
            return
        user.email = new_email
        db.add(user)
        db.commit()
        print(f"Updated {user.username}'s email to {user.email}")

@cli.command()
def create_user(
    username: str = typer.Argument(..., help="The username of the user who you want to create"),
    email: str = typer.Argument(..., help="The email of the new user who you want to create"), 
    password: str = typer.Argument(..., help="The password of the new user you want to create")
):
    """
    This command creates a new user
    """
    with get_session() as db:
        newuser = User(
            username=username,
            email=email,
            password=password
        )
        try:
            db.add(newuser)
            db.commit()
            db.refresh(newuser)
        except IntegrityError as e:
            db.rollback() # let the database undo any previous steps of a transaction
            #print (e.orig) # optionally print the error raised by the database
            print("Username or email already taken!") #give the user a useful message
        else:
            print(newuser) #print the newly created user

@cli.command()
def delete_user(username: str = typer.Argument(..., help="The username of the user you want to delete")):
        """
        This command deletes a specified user
        """
        with get_session() as db:
            user = db.exec(select(User).where(User.username == username)).first()
            if not user:
                print(f"{username} not found! Unable to delete user.")
                return
            db.delete(user)
            db.commit()
            print('{username} deleted')

@cli.command()
def find_user(search: str = typer.Argument(..., help="The input used to search for the user")):
    """
    This command searches for a user via a partial / full match of their username / email
    """
    with get_session() as db:
        all_users = db.exec(select(User)).all()  # get all users
        matching_users = [
            u for u in all_users
            if search in u.username or search in u.email
        ]

        if not matching_users:
            print(f"No users found matching '{search}'")
            return

        for user in matching_users:
            print(user)

@cli.command()
def list_n_users(
    limit: int = typer.Option(10, help="How many users you want to list"), 
    offset: int = typer.Option(0, help="What position of the list you wish to start from")
):
    """
    This command lists the first nth users in the database
    """
    with get_session() as db:
        list = db.exec(select(User).offset(offset).limit(limit)).all()
        if not user:
            print("No users found")
            return
        for user in list:
            print(user)


if __name__ == "__main__":
    cli()