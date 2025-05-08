# Pre-Phase 5 Commit Checklist

This checklist ensures all core functionality is in place before starting Phase 5 (refactoring and abstraction). Security, validation, and sanitization will be handled later.

---

## Core Functionality

- [X] Steam login works and user info is stored correctly.
- [X] Inventory loads properly for logged-in users.
- [X] Users can list inventory items with a custom price.
- [X] "My Listings" page shows user listings and allows price editing.
- [X] Marketplace page displays listings from all users with:
  - [X] Number of listings per item.
  - [X] Starting price per item.

---

## Code Cleanliness

- [ ] No leftover debug code (`print()`, `console.log()`, etc.).
- [ ] No commented-out or test-only code remains.
- [ ] File and function names are clear and consistent.

---

## Database

- [X] `users`, `listings`, and `items` tables contain expected entries.
- [X] No duplicate or irrelevant test entries in live tables.

---

## Pages & Navigation

- [X] All development/testing pages are accessible.
- [X] Data displays correctly on all main pages:
  - [X] Inventory
  - [X] My Listings
  - [X] Marketplace
  - [?] Dev Navigation Page

---

> Next: Begin Phase 5 – Code abstraction, cleanup, and consistent naming.