from __future__ import annotations

from .financial import FinancialQuery, find_latest_financial_report, query_financial_rows
from .jobs import (
    RunRequest,
    enqueue_run_job,
    set_env_for_run,
    write_categories_subset,
    write_merged_system_config,
)
from .logs import tail_file
from .state import read_processing_state
from .status import read_status
from .trace import read_trace_summary
from .cached_products import find_cached_products, read_cached_products
from .linking_map import find_linking_entries, read_linking_map
from .amazon_cache import read_amazon_cache_by_asin
from .run_outputs import get_run_outputs
from .output_writer import write_output_file
from .run_validation import validate_run_integrity
from .repo_files import (
    list_repo_dir,
    read_repo_file,
    enqueue_onboarding_job,
    OnboardingWizardRequest,
)
from .clarify import ClarifyResponse, ask_clarify
from .product_list_refresh import ProductListRefreshRequest, enqueue_product_list_refresh
from .product_list_builder import (
    ProductListBuildRequest,
    build_product_list_from_cached,
    default_product_list_rel_path,
    normalize_product_list_rel_path,
)
from control_plane.checklists import onboarding_sanity_check, run_readiness_check


def _touch_exports() -> None:
    _ = (
        FinancialQuery,
        find_latest_financial_report,
        query_financial_rows,
        RunRequest,
        enqueue_run_job,
        set_env_for_run,
        write_categories_subset,
        write_merged_system_config,
        tail_file,
        read_processing_state,
        read_status,
        read_trace_summary,
        find_cached_products,
        read_cached_products,
        find_linking_entries,
        read_linking_map,
        read_amazon_cache_by_asin,
        get_run_outputs,
        write_output_file,
        validate_run_integrity,
        list_repo_dir,
        read_repo_file,
        enqueue_onboarding_job,
        OnboardingWizardRequest,
        ClarifyResponse,
        ask_clarify,
        ProductListRefreshRequest,
        enqueue_product_list_refresh,
        ProductListBuildRequest,
        build_product_list_from_cached,
        default_product_list_rel_path,
        normalize_product_list_rel_path,
        onboarding_sanity_check,
        run_readiness_check,
    )


_touch_exports()
