from typing import Optional

from sqlalchemy.orm import Session
from loguru import logger

from app.crud.crud_base import CRUDBase
from app.models.sotw import Sotw
from app.models.user import User
from app.schemas.user import UserCreate
from app.schemas.user import UserUpdate
from app.core.security import get_password_hash


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, session: Session, *, email: str) -> Optional[User]:
        """
        Get a user model object from the database with the specified email

        Args:
            session (Session): A SQLAlchemy Session object that is connected to the database.
            email (str): The email of the user being sought after.

        Returns:
            Optional[User]: The user with the given email.
        """
        return session.query(User).filter(User.email == email).first()

    def create(self, session: Session, *, object_in: UserCreate) -> User:
        """
        Creates a User in the database with a hashed password.

        Args:
            session (Session): A SQLAlchemy Session object that is connected to the database.
            object_in (UserCreate): A pydantic model used to create the user.

        Returns:
            User: The newly created user.
        """

        create_data = object_in.model_dump()
        create_data.pop("password")
        db_object = User(**create_data)
        db_object.password = get_password_hash(object_in.password)
        session.add(db_object)
        session.commit()

        return self.get_by_email(session=session, email=db_object.email)

    def add_user_to_sotw(
        self, session: Session, *, db_object: User, object_in: Sotw
    ) -> User:
        """
        Adds the sotw to the user (and vice versa via model relationship)

        Args:
            session (Session): A SQLAlchemy Session object that is connected to the database.
            db_object (User): A model object of the user to update.
            object_in (Sotw): A sotw model object to add to the user.

        Returns:
            User: The newly updated user.
        """
        db_object.sotw_list.append(object_in)
        session.add(db_object)
        session.commit()
        session.refresh(db_object)
        return db_object


user = CRUDUser(User)
