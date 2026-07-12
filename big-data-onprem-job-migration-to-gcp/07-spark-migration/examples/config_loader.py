"""
ConfigLoader — Configuration pattern reference implementation.

Belongs in: dp_spark_common/config/loader.py (shared library)
See: 07-spark-migration/05-configuration-management-and-secrets.md

Merges a job-level YAML config file with secrets resolved from Secret
Manager at runtime, and validates required keys are present. Never
resolves secrets into the YAML file itself, and never logs secret values.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

import yaml


class ConfigError(Exception):
    """Raised when required configuration is missing or invalid."""


class SecretResolver:
    """
    Thin interface over Secret Manager, isolated so it can be swapped
    with a fake/stub in unit tests without needing real GCP credentials.
    """

    def resolve(self, secret_name: str) -> str:
        # Real implementation delegates to google-cloud-secret-manager.
        # Kept as an abstract-ish interface here so tests can inject a
        # FakeSecretResolver instead (see test_example_pricing_job.py).
        from google.cloud import secretmanager

        client = secretmanager.SecretManagerServiceClient()
        name = f"{secret_name}/versions/latest"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")


class FakeSecretResolver(SecretResolver):
    """Test double — returns deterministic fake values, never calls GCP."""

    def __init__(self, values: dict[str, str] | None = None):
        self._values = values or {}

    def resolve(self, secret_name: str) -> str:
        if secret_name not in self._values:
            raise ConfigError(f"No fake value registered for secret '{secret_name}'")
        return self._values[secret_name]


_SECRET_REF_PATTERN = re.compile(r"^secret://(.+)$")


@dataclass
class JobConfig:
    """Typed, validated configuration object passed explicitly into
    pipeline steps — never accessed via global state."""

    env: str
    values: dict[str, Any] = field(default_factory=dict)
    _secret_resolver: SecretResolver = field(default_factory=SecretResolver)

    def get(self, key: str, default: Any = None) -> Any:
        """Dotted-path lookup, e.g. get('pricing.discount_cap_percent')."""
        node: Any = self.values
        for part in key.split("."):
            if not isinstance(node, dict) or part not in node:
                if default is not None:
                    return default
                raise ConfigError(f"Missing required config key: '{key}'")
            node = node[part]
        return node

    def get_secret(self, key: str) -> str:
        """
        Resolve a secret:// reference to its real value via Secret Manager.
        The secret value is never logged or included in repr/str output.
        """
        raw = self.get(key)
        match = _SECRET_REF_PATTERN.match(str(raw))
        if not match:
            raise ConfigError(
                f"Config key '{key}' is not a secret:// reference — "
                f"refusing to resolve a plain value as a secret"
            )
        secret_name = match.group(1)
        return self._secret_resolver.resolve(secret_name)

    def require_keys(self, *keys: str) -> None:
        """Fail fast at job startup if any required key is absent."""
        missing = []
        for key in keys:
            try:
                self.get(key)
            except ConfigError:
                missing.append(key)
        if missing:
            raise ConfigError(
                f"Job cannot start — missing required config keys: {missing}"
            )


class ConfigLoader:
    """Factory for JobConfig — the single entry point job code should use."""

    @staticmethod
    def load(
        env: str,
        job_config_path: str,
        secret_resolver: SecretResolver | None = None,
    ) -> JobConfig:
        with open(job_config_path, "r", encoding="utf-8") as f:
            raw_values = yaml.safe_load(f) or {}

        config = JobConfig(
            env=env,
            values=raw_values,
            _secret_resolver=secret_resolver or SecretResolver(),
        )
        return config
