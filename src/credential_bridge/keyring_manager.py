from typing import Optional, Union

import keyring
from pylogshield import PyLogShield, LogLevel, get_logger
from keyring.errors import KeyringError

from .utils import KeyringManagerError


class KeyringManager:
    """Class for managing credentials using keyring."""

    def __init__(
        self,
        service_name: str = "default_service",
        log_level: Union[LogLevel, str] = LogLevel.WARNING,
        logger: PyLogShield = None,
        mask: bool = True,
    ):
        self.mask = mask
        self.service_name = service_name
        
        # It must use PylogShield because it supports sensitive masking
        if logger and not isinstance(logger, PyLogShield):
            raise KeyringManagerError(
                "logger must be instance of PyLogShield. Please use 'from pylogshield import PyLogShield'"
            )

        self.logger = logger or get_logger(name="credential_bridge", log_level=log_level)

    def __repr__(self) -> str:
        return f"KeyringManager(service_name={self.service_name!r})"

    def add_secret(self, name: str, secret: str) -> None:
        """Add a secret to the keyring."""
        try:
            keyring.set_password(self.service_name, name, secret)
            self.logger.info(
                f"Credentials successfully added: \nSystem: {self.service_name}\nName: {name.capitalize()}\nSecret: {secret}",
                mask=self.mask,
            )
        except KeyringError as e:
            self.logger.error(f"Failed to add {name} for {self.service_name}: {e}")

    def get_secret(self, name: str) -> str:
        """Get a secret from the keyring."""
        try:
            secret = keyring.get_password(self.service_name, name)
            if secret:
                self.logger.info(
                    f"Credentials successfully retrieved: \nSystem: {self.service_name}\nName: {name.capitalize()}\nSecret: {secret}",
                    mask=self.mask,
                )
                return secret
            else:
                self.logger.info(f"No secret found for {name}.")
                return None
        except KeyringError as e:
            self.logger.error(f"Failed to retrieve secret for {name}: {e}")
            # return ""

    def delete_secret(self, name: str) -> None:
        """Delete a secret from the keyring."""
        try:
            keyring.delete_password(self.service_name, name)
            self.logger.info(
                f"Credentials successfully deleted: \nSystem: {self.service_name}\nName: {name.capitalize()}"
            )
        except KeyringError as e:
            self.logger.error(f"Failed to delete {name} for {self.service_name}: {e}")

    def update_secret(self, name: str, secret: str) -> None:
        """Update a secret in the keyring."""
        try:
            existing_secret = keyring.get_password(self.service_name, name)
            if existing_secret:
                keyring.set_password(self.service_name, name, secret)
                self.logger.info(
                    f"Credentials successfully updated: \nSystem: {self.service_name}\nName: {name.capitalize()}\nSecret: {existing_secret}",
                    mask=self.mask,
                )
            else:
                raise KeyringError(f"{name.capitalize()} does not exist")
        except KeyringError as e:
            self.logger.error(f"Failed to update {name} for {self.service_name}: {e}")
