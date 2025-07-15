"""
API endpoints configuration for the application.

This module contains all API endpoint URLs organized by functionality
for consistent and maintainable API calls.
"""

API_BASE = "/api"
DATA_BASE = f"{API_BASE}/data"
IAM_BASE = f"{API_BASE}/iam"

# API Endpoints organized by functionality
API_ENDPOINTS = {
    # Authentication
    "LOGIN": f"{IAM_BASE}/login",
    # Core entities
    "MESH": f"{DATA_BASE}/mesh",
    "SYSTEM": f"{DATA_BASE}/data_system",
    "SOURCE": f"{DATA_BASE}/origin",
    "OBJECT": f"{DATA_BASE}/resource",
    "PRODUCT": f"{DATA_BASE}/product",
    # Linking operations
    "LINK_SYSTEM_TO_SOURCE": f"{DATA_BASE}/link/data_system/origin",
    "LINK_OBJECT_TO_SOURCE": f"{DATA_BASE}/link/origin/resource",
    "LINK_PRODUCT_TO_OBJECT": f"{DATA_BASE}/link/resource/product",
    "LINK_PRODUCT_TO_PRODUCT": f"{DATA_BASE}/link/product/product",
    # Configuration operations
    "CONFIG_CONNECTION_DETAIL_SOURCE": f"{DATA_BASE}/origin/connection",
    "CONFIG_OBJECT": f"{DATA_BASE}/resource/config",
    # Secret management
    "SET_CONNECTION_SECRET": f"{DATA_BASE}/origin/secret",
    # Product operations
    "SCHEMA_PRODUCT": f"{DATA_BASE}/product/schema",
    "TRANSFORMATION_BUILDER": f"{DATA_BASE}/product/compute/builder",
    # Check compute
    "CHECK_COMPUTE": f"{DATA_BASE}/data/compute",
}
