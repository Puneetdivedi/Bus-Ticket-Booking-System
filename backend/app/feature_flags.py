"""Feature flags and configuration management for controlled rollouts."""
from datetime import datetime
from enum import Enum
from typing import Any, dict, Optional

from app.logger import get_logger

logger = get_logger(__name__)


class FeatureStatus(str, Enum):
    """Feature status enumeration."""
    
    DISABLED = "DISABLED"
    ENABLED = "ENABLED"
    BETA = "BETA"
    DEPRECATED = "DEPRECATED"


class Feature:
    """Represent a feature flag."""
    
    def __init__(
        self,
        name: str,
        status: FeatureStatus = FeatureStatus.DISABLED,
        description: str = "",
        rollout_percentage: int = 0,
        enabled_for_users: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ):
        """Initialize feature flag."""
        self.name = name
        self.status = status
        self.description = description
        self.rollout_percentage = max(0, min(100, rollout_percentage))
        self.enabled_for_users = set(enabled_for_users or [])
        self.metadata = metadata or {}
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def is_enabled(self, user_id: Optional[str] = None) -> bool:
        """Check if feature is enabled for user."""
        if self.status == FeatureStatus.DISABLED:
            return False
        
        if self.status == FeatureStatus.ENABLED:
            return True
        
        if user_id and user_id in self.enabled_for_users:
            return True
        
        if self.rollout_percentage >= 100:
            return True
        
        if self.rollout_percentage > 0 and user_id:
            # Consistent rollout based on user ID hash
            user_hash = hash(user_id) % 100
            return user_hash < self.rollout_percentage
        
        return False
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "status": self.status.value,
            "description": self.description,
            "rollout_percentage": self.rollout_percentage,
            "enabled_for_users_count": len(self.enabled_for_users),
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class FeatureFlagManager:
    """Manage application feature flags."""
    
    def __init__(self):
        """Initialize feature flag manager."""
        self.features: dict[str, Feature] = {}
        self._init_default_features()
    
    def _init_default_features(self) -> None:
        """Initialize default features."""
        # Booking features
        self.register_feature(
            "booking_export_csv",
            FeatureStatus.ENABLED,
            "CSV export for bookings",
        )
        self.register_feature(
            "booking_export_json",
            FeatureStatus.BETA,
            "JSON export for bookings",
            rollout_percentage=50,
        )
        self.register_feature(
            "booking_export_xml",
            FeatureStatus.DISABLED,
            "XML export for bookings (coming soon)",
        )
        
        # API features
        self.register_feature(
            "api_metrics_endpoint",
            FeatureStatus.BETA,
            "Metrics endpoint for monitoring",
            rollout_percentage=75,
        )
        self.register_feature(
            "api_backup_endpoint",
            FeatureStatus.BETA,
            "Backup management endpoint",
            rollout_percentage=50,
        )
        
        # Advanced features
        self.register_feature(
            "advanced_rate_limiting",
            FeatureStatus.BETA,
            "Advanced rate limiting",
            rollout_percentage=80,
        )
        self.register_feature(
            "audit_logging",
            FeatureStatus.ENABLED,
            "Audit event logging",
        )
    
    def register_feature(
        self,
        name: str,
        status: FeatureStatus = FeatureStatus.DISABLED,
        description: str = "",
        rollout_percentage: int = 0,
        enabled_for_users: Optional[list[str]] = None,
    ) -> None:
        """Register a feature flag."""
        feature = Feature(
            name=name,
            status=status,
            description=description,
            rollout_percentage=rollout_percentage,
            enabled_for_users=enabled_for_users,
        )
        self.features[name] = feature
        logger.info(f"Feature registered: {name} ({status.value})")
    
    def is_enabled(self, feature_name: str, user_id: Optional[str] = None) -> bool:
        """Check if feature is enabled."""
        if feature_name not in self.features:
            logger.warning(f"Unknown feature: {feature_name}")
            return False
        
        return self.features[feature_name].is_enabled(user_id)
    
    def enable_feature(self, feature_name: str, rollout: int = 100) -> bool:
        """Enable a feature."""
        if feature_name not in self.features:
            return False
        
        feature = self.features[feature_name]
        feature.status = FeatureStatus.ENABLED
        feature.rollout_percentage = rollout
        feature.updated_at = datetime.utcnow()
        logger.info(f"Feature enabled: {feature_name} ({rollout}%)")
        return True
    
    def disable_feature(self, feature_name: str) -> bool:
        """Disable a feature."""
        if feature_name not in self.features:
            return False
        
        feature = self.features[feature_name]
        feature.status = FeatureStatus.DISABLED
        feature.updated_at = datetime.utcnow()
        logger.info(f"Feature disabled: {feature_name}")
        return True
    
    def enable_for_user(self, feature_name: str, user_id: str) -> bool:
        """Enable feature for specific user."""
        if feature_name not in self.features:
            return False
        
        feature = self.features[feature_name]
        feature.enabled_for_users.add(user_id)
        feature.updated_at = datetime.utcnow()
        return True
    
    def disable_for_user(self, feature_name: str, user_id: str) -> bool:
        """Disable feature for specific user."""
        if feature_name not in self.features:
            return False
        
        feature = self.features[feature_name]
        feature.enabled_for_users.discard(user_id)
        feature.updated_at = datetime.utcnow()
        return True
    
    def get_feature_status(self, feature_name: str) -> Optional[dict[str, Any]]:
        """Get feature status details."""
        if feature_name not in self.features:
            return None
        
        return self.features[feature_name].to_dict()
    
    def get_all_features(self) -> dict[str, dict[str, Any]]:
        """Get all features status."""
        return {
            name: feature.to_dict()
            for name, feature in self.features.items()
        }


# Global feature flag manager instance
feature_manager = FeatureFlagManager()


def get_feature_manager() -> FeatureFlagManager:
    """Get global feature flag manager."""
    return feature_manager
