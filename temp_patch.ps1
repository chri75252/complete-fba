$patch = @"
*** Begin Patch
*** Update File: utils/fixed_enhanced_state_manager.py
@@
-    def mark_category_completed(self, category_url: str):
-        """Mark a category as completed - resumption_index now updates continuously"""
-        # Update category completion status
-        if (
-            "gap_processing" in self.state_data
-            and "category_completion_status" in self.state_data["gap_processing"]
-        ):
-            if category_url in self.state_data["gap_processing"]["category_completion_status"]:
-                self.state_data["gap_processing"]["category_completion_status"][category_url][
-                    "status"
-                ] = "FULLY_PROCESSED"
-                self.state_data["gap_processing"]["category_completion_status"][category_url][
-                    "completion_pct"
-                ] = 100.0
-
-        # Legacy subtree deprecated; do not update legacy sections
-
-        # Note: resumption_index now updates continuously via update_processing_progress()
-        # No need to update it here as it's always current
-
-        log.info(f"? Category marked as completed: {category_url[:50]}...")
+    def mark_category_completed(self, category_url: str) -> None:
+        """Mark a category as completed and advance resume pointers."""
+
+        logger = getattr(self, "log", log)
+
+        try:
+            from utils.normalization import normalize_url as _normalize_url
+
+            normalized_url = _normalize_url(category_url) if category_url else category_url
+        except Exception:
+            normalized_url = category_url
+
+        completed_categories = self.state_data.setdefault("completed_categories", [])
+        added_to_completed = False
+        if normalized_url and normalized_url not in completed_categories:
+            completed_categories.append(normalized_url)
+            added_to_completed = True
+
+        # Update gap processing tracker when present
+        gap_processing = self.state_data.get("gap_processing") or {}
+        completion_status = gap_processing.get("category_completion_status") or {}
+        status_entry = completion_status.get(category_url) or completion_status.get(normalized_url)
+        if status_entry is not None:
+            status_entry["status"] = "FULLY_PROCESSED"
+            status_entry["completion_pct"] = 100.0
+
+        # Advance system progression pointers when this is a new completion
+        system_progression = self.state_data.setdefault("system_progression", {})
+        previous_index = system_progression.get("current_category_index", 0)
+
+        if added_to_completed:
+            system_progression["current_category_index"] = previous_index + 1
+            resume_ptr = system_progression.setdefault("resumption_ptr", {})
+            if resume_ptr.get("phase") == "supplier":
+                resume_ptr["cat_idx"] = system_progression["current_category_index"]
+                resume_ptr["prod_idx"] = 0
+
+        if normalized_url:
+            system_progression["current_category_url"] = normalized_url
+        if category_url:
+            system_progression["original_category_url"] = category_url
+
+        self.state_data["last_completed_category"] = normalized_url or category_url or ""
+
+        self.save_state_atomic("mark-category-completed")
+
+        logger.info(
+            "✅ Category completed: url=%s index=%s newly_recorded=%s",
+            (normalized_url or category_url or ""),
+            system_progression.get("current_category_index", 0),
+            added_to_completed,
+        )
*** End Patch
"@
Add-Content -Path temp_patch.ps1 -Value "ApplyPatch -PatchString $patch"
ApplyPatch -PatchString *** Begin Patch
*** Update File: utils/fixed_enhanced_state_manager.py
@@
-    def mark_category_completed(self, category_url: str):
-        """Mark a category as completed - resumption_index now updates continuously"""
-        # Update category completion status
-        if (
-            "gap_processing" in self.state_data
-            and "category_completion_status" in self.state_data["gap_processing"]
-        ):
-            if category_url in self.state_data["gap_processing"]["category_completion_status"]:
-                self.state_data["gap_processing"]["category_completion_status"][category_url][
-                    "status"
-                ] = "FULLY_PROCESSED"
-                self.state_data["gap_processing"]["category_completion_status"][category_url][
-                    "completion_pct"
-                ] = 100.0
-
-        # Legacy subtree deprecated; do not update legacy sections
-
-        # Note: resumption_index now updates continuously via update_processing_progress()
-        # No need to update it here as it's always current
-
-        log.info(f"? Category marked as completed: {category_url[:50]}...")
+    def mark_category_completed(self, category_url: str) -> None:
+        """Mark a category as completed and advance resume pointers."""
+
+        logger = getattr(self, "log", log)
+
+        try:
+            from utils.normalization import normalize_url as _normalize_url
+
+            normalized_url = _normalize_url(category_url) if category_url else category_url
+        except Exception:
+            normalized_url = category_url
+
+        completed_categories = self.state_data.setdefault("completed_categories", [])
+        added_to_completed = False
+        if normalized_url and normalized_url not in completed_categories:
+            completed_categories.append(normalized_url)
+            added_to_completed = True
+
+        # Update gap processing tracker when present
+        gap_processing = self.state_data.get("gap_processing") or {}
+        completion_status = gap_processing.get("category_completion_status") or {}
+        status_entry = completion_status.get(category_url) or completion_status.get(normalized_url)
+        if status_entry is not None:
+            status_entry["status"] = "FULLY_PROCESSED"
+            status_entry["completion_pct"] = 100.0
+
+        # Advance system progression pointers when this is a new completion
+        system_progression = self.state_data.setdefault("system_progression", {})
+        previous_index = system_progression.get("current_category_index", 0)
+
+        if added_to_completed:
+            system_progression["current_category_index"] = previous_index + 1
+            resume_ptr = system_progression.setdefault("resumption_ptr", {})
+            if resume_ptr.get("phase") == "supplier":
+                resume_ptr["cat_idx"] = system_progression["current_category_index"]
+                resume_ptr["prod_idx"] = 0
+
+        if normalized_url:
+            system_progression["current_category_url"] = normalized_url
+        if category_url:
+            system_progression["original_category_url"] = category_url
+
+        self.state_data["last_completed_category"] = normalized_url or category_url or ""
+
+        self.save_state_atomic("mark-category-completed")
+
+        logger.info(
+            "✅ Category completed: url=%s index=%s newly_recorded=%s",
+            (normalized_url or category_url or ""),
+            system_progression.get("current_category_index", 0),
+            added_to_completed,
+        )
*** End Patch
