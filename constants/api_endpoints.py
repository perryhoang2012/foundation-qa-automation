"""
API endpoints configuration for the application.

This module contains all API endpoint URLs organized by functionality
for consistent and maintainable API calls.
"""

API_ENDPOINTS = {
    # Authentication
    "LOGIN": f"/api/iam/login",
    # Core entities
    "MESH": f"/api/data/mesh",
    "SYSTEM": f"/api/data/data_system",
    "SOURCE": f"/api/data/origin",
    "OBJECT": f"/api/data/resource",
    "PRODUCT": f"/api/data/product",
    # Linking operations
    "LINK_SYSTEM_TO_SOURCE": f"/api/data/link/data_system/origin",
    "LINK_OBJECT_TO_SOURCE": f"/api/data/link/origin/resource",
    "LINK_PRODUCT_TO_OBJECT": f"/api/data/link/resource/product",
    "LINK_PRODUCT_TO_PRODUCT": f"/api/data/link/product/product",
    # Configuration operations
    "CONFIG_CONNECTION_DETAIL_SOURCE": f"/api/data/origin/connection",
    "CONFIG_OBJECT": f"/api/data/resource/config",
    # Secret management
    "SET_CONNECTION_SECRET": f"/api/data/origin/secret",
    # Product operations
    "SCHEMA_PRODUCT": f"/api/data/product/schema",
    "TRANSFORMATION_BUILDER": f"/api/data/product/compute/builder",
    # Check compute
    "CHECK_COMPUTE": f"/api/data/data/compute",
}
