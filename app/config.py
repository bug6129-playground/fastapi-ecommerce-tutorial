"""
FastAPI E-Commerce Tutorial - Configuration Management
=====================================================

This module loads configuration from YAML files, providing a clean and flexible
approach to managing application settings. Users can easily modify settings
without changing any code - just edit the config.yaml file!

Key Features:
- YAML-based configuration (user-friendly)
- Environment-specific overrides
- Type validation using Pydantic
- Default values with clear documentation
- Easy to modify without code changes

Author: bug6129
"""

import yaml
from pathlib import Path
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, validator


class AppConfig(BaseModel):
    """Application-level configuration settings."""
    name: str = "FastAPI E-Commerce API"
    version: str = "1.0.0"
    description: str = "A comprehensive e-commerce API built with FastAPI"
    environment: str = "development"
    debug: bool = True


class ServerConfig(BaseModel):
    """Server configuration settings."""
    host: str = "127.0.0.1"
    port: int = 8000
    reload: bool = True
    
    @validator('port')
    def validate_port(cls, v):
        """Ensure port is in valid range."""
        if not (1024 <= v <= 65535):
            raise ValueError('Port must be between 1024 and 65535')
        return v


class DatabaseConfig(BaseModel):
    """Database configuration settings."""
    host: str = "localhost"
    port: int = 5432
    name: str = "fastapi_ecommerce"
    username: str = "fastapi_user"
    password: str = "changeme"
    pool_size: int = 20
    max_overflow: int = 0
    pool_timeout: int = 30
    test_db_name: str = "fastapi_ecommerce_test"
    
    @property
    def url(self) -> str:
        """Get the complete database URL."""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.name}"
    
    @property
    def async_url(self) -> str:
        """Get the async database URL for asyncpg."""
        return f"postgresql+asyncpg://{self.username}:{self.password}@{self.host}:{self.port}/{self.name}"
    
    @property
    def test_url(self) -> str:
        """Get the test database URL."""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.test_db_name}"


class SecurityConfig(BaseModel):
    """Security-related configuration settings."""
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    bcrypt_rounds: int = 12
    
    @validator('secret_key')
    def validate_secret_key(cls, v):
        """Ensure secret key is long enough."""
        if len(v) < 32:
            raise ValueError('Secret key must be at least 32 characters long')
        return v
    
    @validator('bcrypt_rounds')
    def validate_bcrypt_rounds(cls, v):
        """Ensure bcrypt rounds are in safe range."""
        if not (4 <= v <= 16):
            raise ValueError('Bcrypt rounds must be between 4 and 16')
        return v


class CorsConfig(BaseModel):
    """CORS (Cross-Origin Resource Sharing) configuration."""
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    allowed_methods: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allowed_headers: List[str] = ["*"]
    allow_credentials: bool = True


class FileUploadConfig(BaseModel):
    """File upload configuration settings."""
    max_size_mb: int = 5
    allowed_extensions: List[str] = ["jpg", "jpeg", "png", "gif", "webp"]
    upload_directory: str = "uploads"
    
    @property
    def max_size_bytes(self) -> int:
        """Get maximum file size in bytes."""
        return self.max_size_mb * 1024 * 1024
    
    @property
    def upload_path(self) -> Path:
        """Get the upload directory as a Path object."""
        path = Path(self.upload_directory)
        path.mkdir(exist_ok=True)  # Create directory if it doesn't exist
        return path


class EmailConfig(BaseModel):
    """Email configuration settings."""
    smtp_server: Optional[str] = None
    smtp_port: int = 587
    username: Optional[str] = None
    password: Optional[str] = None
    from_address: str = "noreply@fastapi-ecommerce.com"
    use_tls: bool = True


class LoggingConfig(BaseModel):
    """Logging configuration settings."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: Optional[str] = None
    max_file_size_mb: int = 10
    backup_count: int = 5
    
    @validator('level')
    def validate_log_level(cls, v):
        """Ensure log level is valid."""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'Log level must be one of: {", ".join(valid_levels)}')
        return v.upper()


class DocsConfig(BaseModel):
    """API documentation configuration."""
    title: str = "FastAPI E-Commerce API"
    description: str = "A comprehensive e-commerce API built with FastAPI"
    version: str = "1.0.0"
    contact: Dict[str, str] = {"name": "bug6129", "email": "support@example.com"}
    license: Dict[str, str] = {"name": "MIT", "url": "https://opensource.org/licenses/MIT"}


class RateLimitingConfig(BaseModel):
    """Rate limiting configuration."""
    enabled: bool = True
    requests_per_minute: int = 60
    requests_per_hour_user: int = 1000


class FeaturesConfig(BaseModel):
    """Feature flags configuration."""
    enable_user_registration: bool = True
    enable_email_verification: bool = False
    enable_password_reset: bool = True
    enable_file_upload: bool = True
    enable_order_tracking: bool = True
    enable_customer_support: bool = True
    enable_product_reviews: bool = True
    enable_wishlist: bool = False
    enable_coupons: bool = False
    enable_inventory_tracking: bool = True


class Settings(BaseModel):
    """
    Main settings class that combines all configuration sections.
    
    This class loads configuration from YAML files and provides
    a clean interface to all application settings.
    """
    app: AppConfig = AppConfig()
    server: ServerConfig = ServerConfig()
    database: DatabaseConfig = DatabaseConfig()
    security: SecurityConfig = SecurityConfig()
    cors: CorsConfig = CorsConfig()
    file_upload: FileUploadConfig = FileUploadConfig()
    email: EmailConfig = EmailConfig()
    logging: LoggingConfig = LoggingConfig()
    docs: DocsConfig = DocsConfig()
    rate_limiting: RateLimitingConfig = RateLimitingConfig()
    features: FeaturesConfig = FeaturesConfig()
    
    # Additional configuration sections can be added as needed
    # payments: PaymentsConfig = PaymentsConfig()
    # cache: CacheConfig = CacheConfig()
    
    @classmethod
    def load_from_yaml(cls, config_file: str = "config.yaml") -> "Settings":
        """
        Load configuration from YAML file.
        
        Args:
            config_file (str): Path to the YAML configuration file
            
        Returns:
            Settings: Configured Settings instance
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If YAML is invalid
            ValueError: If configuration values are invalid
            
        Example:
            settings = Settings.load_from_yaml("config.yaml")
            print(settings.server.port)  # 8000
            print(settings.database.url)  # postgresql://...
        """
        config_path = Path(config_file)
        
        if not config_path.exists():
            raise FileNotFoundError(
                f"Configuration file '{config_file}' not found. "
                f"Please create it or copy from config.yaml.example"
            )
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Error parsing YAML configuration: {e}")
        
        if not config_data:
            raise ValueError("Configuration file is empty")
        
        # Create settings instance with loaded data
        return cls(**config_data)
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.app.environment.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.app.environment.lower() == "production"
    
    def is_feature_enabled(self, feature_name: str) -> bool:
        """
        Check if a specific feature is enabled.
        
        Args:
            feature_name (str): Name of the feature to check
            
        Returns:
            bool: True if feature is enabled, False otherwise
            
        Example:
            if settings.is_feature_enabled("enable_user_registration"):
                # Handle user registration
                pass
        """
        return getattr(self.features, feature_name, False)


def load_settings(config_file: str = "config.yaml") -> Settings:
    """
    Load application settings from YAML configuration.
    
    This is a convenience function that loads the configuration and handles
    common errors gracefully, providing helpful error messages for users.
    
    Args:
        config_file (str): Path to configuration file
        
    Returns:
        Settings: Loaded configuration settings
        
    Example:
        from app.config import load_settings
        
        settings = load_settings()
        app = FastAPI(title=settings.docs.title)
    """
    try:
        return Settings.load_from_yaml(config_file)
    except FileNotFoundError as e:
        print(f"❌ Configuration Error: {e}")
        print("\n💡 Quick Fix:")
        print(f"   1. Make sure '{config_file}' exists in your project root")
        print("   2. Copy the example configuration: cp config.yaml.example config.yaml")
        print("   3. Edit the configuration file to match your setup")
        raise
    except yaml.YAMLError as e:
        print(f"❌ YAML Error: {e}")
        print("\n💡 Quick Fix:")
        print("   1. Check your YAML syntax (indentation, colons, etc.)")
        print("   2. Use a YAML validator online to check your file")
        print("   3. Compare with the example configuration file")
        raise
    except ValueError as e:
        print(f"❌ Configuration Value Error: {e}")
        print("\n💡 Quick Fix:")
        print("   1. Check the configuration values in your YAML file")
        print("   2. Ensure all required fields are present")
        print("   3. Verify data types match expected format")
        raise


def get_database_url(async_mode: bool = False, test_mode: bool = False) -> str:
    """
    Get database URL for different modes.
    
    Args:
        async_mode (bool): Return async URL for asyncpg
        test_mode (bool): Return test database URL
        
    Returns:
        str: Database connection URL
        
    Example:
        # Normal database URL
        url = get_database_url()
        
        # Async database URL
        async_url = get_database_url(async_mode=True)
        
        # Test database URL
        test_url = get_database_url(test_mode=True)
    """
    settings = load_settings()
    
    if test_mode:
        return settings.database.test_url
    elif async_mode:
        return settings.database.async_url
    else:
        return settings.database.url


# Create global settings instance
# This will be imported and used throughout the application
settings = load_settings()


# Utility functions for common configuration tasks
# ===============================================

def is_file_extension_allowed(filename: str) -> bool:
    """
    Check if file extension is allowed for upload.
    
    Args:
        filename (str): Name of the file
        
    Returns:
        bool: True if extension is allowed
        
    Example:
        if is_file_extension_allowed("photo.jpg"):
            # Process the upload
            pass
    """
    if '.' not in filename:
        return False
    
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in settings.file_upload.allowed_extensions


def get_upload_path(filename: str) -> Path:
    """
    Get full path for uploaded file.
    
    Args:
        filename (str): Name of the file
        
    Returns:
        Path: Full path where file should be stored
        
    Example:
        file_path = get_upload_path("photo.jpg")
        # Returns: uploads/photo.jpg
    """
    return settings.file_upload.upload_path / filename


# Export commonly used items
__all__ = [
    'Settings',
    'settings',
    'load_settings',
    'get_database_url',
    'is_file_extension_allowed',
    'get_upload_path'
]


# Development helper
if __name__ == "__main__":
    """
    Print current configuration when run directly.
    Useful for debugging and verifying configuration.
    
    Usage:
        python -m app.config
    """
    try:
        config = load_settings()
        print("🚀 FastAPI E-Commerce Configuration")
        print("=" * 50)
        print(f"📱 App Name: {config.app.name}")
        print(f"🌍 Environment: {config.app.environment}")
        print(f"🐛 Debug Mode: {config.app.debug}")
        print(f"🌐 Server: {config.server.host}:{config.server.port}")
        print(f"🗄️  Database: {config.database.host}:{config.database.port}/{config.database.name}")
        print(f"📁 Upload Directory: {config.file_upload.upload_directory}")
        print(f"📏 Max File Size: {config.file_upload.max_size_mb} MB")
        print(f"🔒 Security: JWT with {config.security.algorithm}")
        print(f"📊 Rate Limiting: {config.rate_limiting.requests_per_minute}/min")
        print("=" * 50)
        print("✅ Configuration loaded successfully!")
        
        # Print enabled features
        enabled_features = []
        for field_name, field_value in config.features.dict().items():
            if field_value:
                feature_name = field_name.replace('enable_', '').replace('_', ' ').title()
                enabled_features.append(feature_name)
        
        if enabled_features:
            print(f"\n🎯 Enabled Features: {', '.join(enabled_features)}")
            
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        exit(1)