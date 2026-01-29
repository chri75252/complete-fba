from __future__ import annotations


def supplier_domain_to_underscore(supplier_domain: str) -> str:
    return supplier_domain.replace(".", "_")


def supplier_domain_to_hyphen(supplier_domain: str) -> str:
    return supplier_domain.replace(".", "-")
