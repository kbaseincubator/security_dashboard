import os
from datetime import datetime

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_ORG = "kbase"
GITHUB_API_URL = "https://api.github.com"
HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}
TODAY = datetime.now().strftime("%Y-%m-%d")
CACHE_DIR = os.getcwd() + "/cache"
REPORTS_DIR = os.getcwd() + "/reports"

CORE_REPOS = [
    "kbase/auth2",
    "jgi-kbase/AssemblyHomologyService",
    "kbase/execution_engine2",
    "kbase/blobstore",
    "kbase/file_cache_server",
    "kbase/catalog",
    "kbase/collections",
    "kbase/data_import_export",
    "kbase/feeds",
    "kbase/groups",
    "jgi-kbase/IDMappingService",
    "kbase/handle_service2",
    "kbase/narrative_method_store",
    "kbase/relation_engine",
    "kbase/staging_service",
    "kbaseapps/sketch_service",
    "kbase/sample_service",
    "kbase/search_api2",
    "kbase/service_wizard",
    "kbase/user_profile",
    "kbase/workspace_deluxe",
    "kbase/kb_sdk",
    "kbase/narrative",
    "kbase/narrative-traefiker"
]
