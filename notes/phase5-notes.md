Understood. Here's the same content rewritten in a clean, copy-pasteable Markdown format — no tables, no fluff, just realistic developer documentation.

---

# Phase 5 – Naming Conventions and Code Structure

This document outlines naming conventions and structural guidelines used across the backend (Python/Flask) and frontend (JavaScript) of the CS2 marketplace project.

## Python

Use `snake_case` for all variables, functions, and filenames.

Use descriptive, intent-revealing prefixes to indicate what the function does:

* `fetch_`: External API calls
  Example: `fetch_steam_inventory()`

* `get_`: Database queries that return data
  Example: `get_user_by_id()`

* `build_`: Functions that return filtered database queries
  Example: `build_listings_by_seller()`

* `insert_`: Direct database inserts (low-level)
  Example: `insert_listing()`

* `update_`: Direct database updates
  Example: `update_listing_price()`

* `delete_`: Direct database deletes
  Example: `delete_user_listing()`

* `create_`: High-level creation logic (may include validation, etc.)
  Example: `create_listing()`

* `edit_`: High-level edit logic
  Example: `edit_user_profile()`

* `remove_`: High-level delete logic
  Example: `remove_expired_listings()`

* `send_`: Used for outbound actions like sending trade offers
  Example: `send_trade_offer()`

* `parse_`: Used for transforming or cleaning raw data
  Example: `parse_inventory_response()`

* `build_`: Used to construct payloads or queries
  Example: `build_trade_payload()`

* `is_`, `has_`: Boolean checks
  Example: `is_trade_valid()`, `has_items()`

Special distinction:

* `asset_id` = internal ID from our platform's static items table
* `assetid` = Steam inventory's unique item ID (not interchangeable)

## JavaScript

Use `camelCase` for all variables and functions.

Use similar prefixing to Python:

* `fetchInventory()`
* `getUser()`, `setUser()`
* `handleClick()`
* `isTradable()`, `hasSelectedItem()`
* `renderInventoryGrid()`

## Function Layering

### Low-level function (Flask SQLAlchemy example)

Directly interacts with the database.

```python
def insert_listing(user_id, asset_id, price, float_value):
    new_listing = Listing(
        user_id=user_id,
        asset_id=asset_id,
        price=price,
        float_value=float_value
    )
    db.session.add(new_listing)
    db.session.commit()
```

### High-level function

Wraps logic, handles validation or flow control, and calls lower-level functions.

```python
def create_listing(user_id, item_data):
    if "asset_id" not in item_data or "price" not in item_data:
        raise ValueError("Missing required fields")

    asset_id = item_data["asset_id"]
    price = item_data["price"]
    float_value = item_data.get("float", 0.0)

    existing = Listing.query.filter_by(user_id=user_id, asset_id=asset_id).first()
    if existing:
        raise ValueError("Listing already exists")

    insert_listing(user_id, asset_id, price, float_value)
```

## Summary

* Use `snake_case` for Python and `camelCase` for JavaScript.
* Prefix functions clearly to reflect purpose.
* Keep low-level DB functions simple and separate from logic-heavy functions.
* Always distinguish between `asset_id` (internal) and `assetid` (Steam-specific).

---
| Context         | Example             | Style               | Notes                       |
| --------------- | ------------------- | ------------------- | --------------------------- |
| Variables       | `user_name`         | **snake\_case**     | PEP 8 convention            |
| Functions       | `save_data()`       | snake\_case         |                             |
| Constants       | `API_URL`           | UPPER\_SNAKE\_CASE  |                             |
| Class names     | `class UserAccount` | PascalCase          |                             |
| Dictionary keys | `'user_name'`       | usually snake\_case | Matches DB or Python naming |

| Context                | Example                      | Style              | Notes                     |
| ---------------------- | ---------------------------- | ------------------ | ------------------------- |
| Variables              | `let userName`               | **camelCase**      | JS convention             |
| Functions              | `function saveData()`        | camelCase          | JS convention             |
| Constants              | `const API_URL`              | UPPER\_SNAKE\_CASE | For global constants      |
| Object keys (custom)   | `user.name`                  | camelCase          | JS-style objects          |
| DOM IDs/Classes Access | `getElementById("userName")` | Matches HTML       | Keep consistent with HTML |

| Context                 | Example         | Style                         | Notes                            |
| ----------------------- | --------------- | ----------------------------- | -------------------------------- |
| Standard attributes     | `autocomplete`  | lowercase                     | Always lowercase                 |
| Custom data attributes  | `data-user-id`  | **kebab-case**                | Used for embedding custom data   |
| Element IDs and classes | `id="userName"` | often camelCase or kebab-case | Up to you — just stay consistent |
