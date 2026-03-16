# REVERT_TRACKING.md

## Scope & Reason
- Reason: ui_redesign_20260315
- Objective: Re-align the dashboard UI with Stitch-generated Precision Dashboard v2, add more Auto Refresh options (3s, 5s), and incorporate ui-ux-pro-max guidelines.

## Targeted Files & Backup Strategy
1. **dashboard_v2/templates/index.html**
   - *Intended Scope*: Add Auto-Refresh options; embed Tailwind configuration with Stitch tokens; apply 'Kinetic Vault' structural UI changes (Glass & Gradient rules, No-Line rule).
   - *Backup Path*: `dashboard/templates/index.html` (Original preserved entirely in the root `dashboard/` directory)
2. **dashboard_v2/static/css/styles.css**
   - *Intended Scope*: Refine component primitives, input fields, fonts (`Space Grotesk`, `Manrope`), text contrasts, active/hover states.
   - *Backup Path*: `dashboard/static/css/styles.css`

## Edit Order
1. Revert failed edit on `dashboard/templates/index.html` (Done).
2. Create isolated `dashboard_v2/` working directory (Done).
3. Introduce `3s` and `5s` dropdown options into `dashboard_v2/templates/index.html`.
4. Apply `<script id="tailwind-config">` configurations into `index.html`.
5. Adopt new UI layout changes to `index.html` referencing Stitch generated layouts (`surface-container`, glass text effects, layout gaps).
6. Tweak `styles.css` using `ui-ux-pro-max` search outputs for component aesthetics.

## Planned Validation
- Verify `dashboard_v2` UI structure visually.
- Evaluate against "Anti-patterns" checklist from `ui-ux-pro-max` guidelines (no emojis, stable hover states, sufficient contrast ratio, no default cursors, glass background transparency >0).
- Launch Streamlit / Web Application locally to assert DOM integrity.
- Request explicit USER Review.
