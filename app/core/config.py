from pathlib import Path
from typing import Any, Dict, List

import yaml
from pydantic import BaseSettings


def yaml_config_settings_source(settings: BaseSettings) -> Dict[str, Any]:
    yaml_file = getattr(settings.__config__, "yaml_file", "")

    assert yaml_file, "Settings.yaml_file not properly configured"

    path = Path(yaml_file)

    if not path.exists():
        raise FileNotFoundError(f"Could not open yaml settings file at: {path}")
    return yaml.safe_load(path.read_text("utf-8"))


class WenXin(BaseSettings):
    base_url: str
    chat_completion_path: str
    access_token: str


class Config(BaseSettings):
    wenxin: WenXin
    token: List[str]

    class Config:
        yaml_file = Path("config").resolve().joinpath("config.yaml")
        case_sensitive = True

        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):
            return (
                init_settings,
                yaml_config_settings_source,
                env_settings,
            )


config = Config()


wenxin = config.wenxin
token = config.token
