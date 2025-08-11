"""
E-Commerce API Configuration Management
======================================

This module handles loading and managing configuration from YAML files.
It provides type-safe configuration classes and easy access to settings.

Author: bug6129
"""

import yaml
from pathlib import Path
from typing import List, Dict, Any
from pydantic import BaseModel


class AppConfig(BaseModel):
    """Application configuration settings."""
    name: str
    version: str
    description: str
    environment: str
    debug: bool


class ServerConfig(BaseModel):
    """Server configuration settings."""
    host: str
    port: int
    reload: bool


class DocsConfig(BaseModel):
    """API documentation configuration."""
    title: str
    description: str
    version: str
    contact: Dict[str, str]
    license: Dict[str, str]


class CorsConfig(BaseModel):
    """CORS configuration settings."""
    allowed_origins: List[str]
    allowed_methods: List[str]
    allowed_headers: List[str]
    allow_credentials: bool


class FeaturesConfig(BaseModel):
    """Feature flags configuration."""
    enable_user_registration: bool
    enable_product_catalog: bool
    enable_shopping_cart: bool
    enable_order_processing: bool
    enable_customer_support: bool


class BusinessConfig(BaseModel):
    """Business logic configuration."""
    currency: str
    tax_rate: float
    free_shipping_threshold: float
    max_cart_items: int
    order_timeout_minutes: int


class DevelopmentConfig(BaseModel):
    """Development-specific configuration."""
    create_sample_data: bool
    log_sql_queries: bool
    cors_allow_all: bool


class Settings(BaseModel):
    """Main configuration class that combines all settings."""
    app: AppConfig
    server: ServerConfig
    docs: DocsConfig
    cors: CorsConfig
    features: FeaturesConfig
    business: BusinessConfig
    development: DevelopmentConfig

    @classmethod
    def load_from_yaml(cls, config_file: str = "config.yaml") -> "Settings":
        """
        Load configuration from YAML file.
        
        Args:
            config_file: Path to the YAML configuration file
            
        Returns:
            Settings: Loaded configuration
        """
        config_path = Path(config_file)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file '{config_file}' not found")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        return cls(**config_data)
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.app.environment.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.app.environment.lower() == "production"


# Global settings instance
settings = Settings.load_from_yaml()