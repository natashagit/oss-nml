"""Database module for storing user credentials securely.

This module handles the PostgreSQL database connection and provides
methods to store and retrieve encrypted user credentials.
"""

import logging
import os
from datetime import UTC, datetime

from cryptography.fernet import Fernet
from sqlalchemy import Column, DateTime, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

logger = logging.getLogger(__name__)

Base = declarative_base()


class UserCredential(Base):
    """SQLAlchemy model for storing user credentials.

    Attributes:
        user_id: Unique identifier from Google OAuth (primary key).
        email: User's email from Google OAuth.
        google_refresh_token: Encrypted Google OAuth refresh token.
        openai_api_key: Encrypted OpenAI API key.
        created_at: Timestamp when the credential was created.
        updated_at: Timestamp when the credential was last updated.

    """

    __tablename__ = "user_credentials"

    user_id = Column(String(255), primary_key=True)
    email = Column(String(255), nullable=False, unique=True)
    google_refresh_token = Column(Text, nullable=True)
    openai_api_key = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )


class CredentialStore:
    """Manages encrypted storage and retrieval of user credentials.

    This class handles database operations and encryption/decryption
    of sensitive credentials using Fernet symmetric encryption.

    Environment Variables:
        DATABASE_URL: PostgreSQL connection string.
        ENCRYPTION_KEY: Base64-encoded Fernet encryption key.
    """

    def __init__(self, database_url: str | None = None, encryption_key: str | None = None) -> None:
        """Initialize the credential store.

        Args:
            database_url: PostgreSQL connection string (or from DATABASE_URL env var).
            encryption_key: Base64-encoded Fernet key (or from ENCRYPTION_KEY env var).

        """
        self.database_url = database_url or os.environ.get(
            "DATABASE_URL",
            "postgresql://localhost/openai_service",
        )
        self.encryption_key = encryption_key or os.environ.get("ENCRYPTION_KEY")

        if not self.encryption_key:
            logger.warning(
                "No ENCRYPTION_KEY found. Generating a new one. "
                "This should only happen in development!",
            )
            self.encryption_key = Fernet.generate_key().decode()

        self.cipher = Fernet(self.encryption_key.encode())
        self.engine = create_engine(self.database_url)
        Base.metadata.create_all(self.engine)
        self.session_factory = sessionmaker(bind=self.engine)

    def _encrypt(self, data: str) -> str:
        """Encrypt a string using Fernet encryption."""
        return self.cipher.encrypt(data.encode()).decode()

    def _decrypt(self, encrypted_data: str) -> str:
        """Decrypt a Fernet-encrypted string."""
        return self.cipher.decrypt(encrypted_data.encode()).decode()

    def store_user_credentials(
        self,
        user_id: str,
        email: str,
        google_refresh_token: str | None = None,
        openai_api_key: str | None = None,
    ) -> None:
        """Store or update user credentials in the database.

        Args:
            user_id: Unique user identifier from Google OAuth.
            email: User's email address.
            google_refresh_token: Google OAuth refresh token (will be encrypted).
            openai_api_key: OpenAI API key (will be encrypted).

        """
        session = self.session_factory()
        try:
            user_cred = session.query(UserCredential).filter_by(user_id=user_id).first()

            encrypted_google_token = (
                self._encrypt(google_refresh_token) if google_refresh_token else None
            )
            encrypted_openai_key = self._encrypt(openai_api_key) if openai_api_key else None

            if user_cred:
                # Update existing record
                user_cred.email = email
                if encrypted_google_token:
                    user_cred.google_refresh_token = encrypted_google_token
                if encrypted_openai_key:
                    user_cred.openai_api_key = encrypted_openai_key
                user_cred.updated_at = datetime.now(UTC)
            else:
                # Create new record
                user_cred = UserCredential(
                    user_id=user_id,
                    email=email,
                    google_refresh_token=encrypted_google_token,
                    openai_api_key=encrypted_openai_key,
                )
                session.add(user_cred)

            session.commit()
            logger.info("Stored credentials for user %s", user_id)
        except Exception:
            session.rollback()
            logger.exception("Failed to store credentials for user %s", user_id)
            raise
        finally:
            session.close()

    def get_openai_api_key(self, user_id: str) -> str | None:
        """Retrieve and decrypt the OpenAI API key for a user.

        Args:
            user_id: The unique user identifier.

        Returns:
            Decrypted OpenAI API key or None if not found.

        """
        session = self.session_factory()
        try:
            user_cred = session.query(UserCredential).filter_by(user_id=user_id).first()
            if user_cred and user_cred.openai_api_key:
                return self._decrypt(user_cred.openai_api_key)
            return None
        finally:
            session.close()

    def get_google_refresh_token(self, user_id: str) -> str | None:
        """Retrieve and decrypt the Google refresh token for a user.

        Args:
            user_id: The unique user identifier.

        Returns:
            Decrypted Google refresh token or None if not found.

        """
        session = self.session_factory()
        try:
            user_cred = session.query(UserCredential).filter_by(user_id=user_id).first()
            if user_cred and user_cred.google_refresh_token:
                return self._decrypt(user_cred.google_refresh_token)
            return None
        finally:
            session.close()

    def user_exists(self, user_id: str) -> bool:
        """Check if a user exists in the database.

        Args:
            user_id: The unique user identifier.

        Returns:
            True if the user exists, False otherwise.

        """
        session = self.session_factory()
        try:
            return session.query(UserCredential).filter_by(user_id=user_id).first() is not None
        finally:
            session.close()
