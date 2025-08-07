"""
Hash-based Lookup Methods for Linking Map Performance Optimization
These methods should be added to the PassiveExtractionWorkflow class
"""

def _add_to_linking_map_indexes(self, entry):
    """Add entry to hash indexes for O(1) lookups"""
    supplier_ean = entry.get("supplier_ean")
    supplier_url = entry.get("supplier_url")
    
    if supplier_ean:
        self._linking_map_ean_index[supplier_ean] = entry
    if supplier_url:
        self._linking_map_url_index[supplier_url] = entry

def _remove_from_linking_map_indexes(self, entry):
    """Remove entry from hash indexes"""
    supplier_ean = entry.get("supplier_ean")
    supplier_url = entry.get("supplier_url")
    
    if supplier_ean and supplier_ean in self._linking_map_ean_index:
        del self._linking_map_ean_index[supplier_ean]
    if supplier_url and supplier_url in self._linking_map_url_index:
        del self._linking_map_url_index[supplier_url]

def _rebuild_linking_map_indexes(self):
    """Rebuild hash indexes from current linking map"""
    self._linking_map_ean_index.clear()
    self._linking_map_url_index.clear()
    
    for entry in self.linking_map:
        self._add_to_linking_map_indexes(entry)

def _check_product_in_linking_map(self, supplier_ean, supplier_url):
    """Fast O(1) lookup to check if product exists in linking map"""
    if supplier_ean and supplier_ean in self._linking_map_ean_index:
        return True, self._linking_map_ean_index[supplier_ean]
    elif supplier_url and supplier_url in self._linking_map_url_index:
        return True, self._linking_map_url_index[supplier_url]
    return False, None

def _add_linking_map_entry_with_index(self, entry):
    """Add entry to linking map and update indexes"""
    self.linking_map.append(entry)
    self._add_to_linking_map_indexes(entry)