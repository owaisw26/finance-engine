from app.core.config import Settings


def test_settings_can_be_overridden() -> None:
    settings = Settings(app_env="test", api_port=9000, ai_provider="fallback")

    assert settings.app_env == "test"
    assert settings.api_port == 9000
    assert settings.ai_provider == "fallback"
