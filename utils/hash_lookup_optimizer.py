def add_entry(self, entry: Dict[str, Any]) -> bool:
    """Add a new entry to the indexes if not already present.

    Args:
        entry: Linking map entry to add or update

    Returns:
        bool: ``True`` if the entry was added as new, ``False`` if a duplicate
        was found and the existing record was updated.
    """
    with self._lock:
        if not self._index_valid:
            # Without built indexes we can't check for duplicates; simply add
            self._add_entry_to_indexes(entry)
            self.logger.debug(
                f"✅ Added entry to hash indexes: {entry.get('supplier_ean', 'No EAN')}"
            )
            return True

        supplier_ean = entry.get("supplier_ean") or entry.get("ean")
        supplier_url = entry.get("supplier_url") or entry.get("url")

        existing_entry: Optional[Dict[str, Any]] = None
        if supplier_ean and supplier_ean in self._ean_index:
            existing_entry = self._ean_index[supplier_ean]
        elif supplier_url and supplier_url in self._url_index:
            existing_entry = self._url_index[supplier_url]

        if existing_entry:
            # Update existing record in place so linking_map reference stays valid
            existing_entry.update(entry)
            # Refresh indexes in case key fields changed
            self._add_entry_to_indexes(existing_entry)
            self.logger.debug(
                f"🔄 Duplicate detected - updated existing entry: {supplier_url or supplier_ean}"
            )
            return False

        self._add_entry_to_indexes(entry)
        self.logger.debug(
            f"✅ Added entry to hash indexes: {supplier_ean or supplier_url or 'No Key'}"
        )
        return True
