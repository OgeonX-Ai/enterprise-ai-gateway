from dataclasses import dataclass
from typing import Optional

from ...settings import Settings


@dataclass
class ServiceNowConfig:
    instance_url: Optional[str]
    auth_mode: str
    username: Optional[str]
    password: Optional[str]
    client_id: Optional[str]
    client_secret: Optional[str]
    token_url: Optional[str]
    mock_mode: bool

    @classmethod
    def from_settings(cls, settings: Settings) -> "ServiceNowConfig":
        instance_url = settings.servicenow_instance_url
        username = settings.servicenow_username
        password = settings.servicenow_password
        client_id = settings.servicenow_client_id
        client_secret = settings.servicenow_client_secret
        token_url = settings.servicenow_token_url
        auth_mode = settings.servicenow_auth_mode

        creds_present = all([instance_url, username, password])
        mock_env_flag = settings.servicenow_mock_mode
        mock_mode = mock_env_flag or not creds_present

        return cls(
            instance_url=instance_url,
            auth_mode=auth_mode,
            username=username,
            password=password,
            client_id=client_id,
            client_secret=client_secret,
            token_url=token_url,
            mock_mode=mock_mode,
        )

    @property
    def mode_label(self) -> str:
        return "mock" if self.mock_mode else "real"
