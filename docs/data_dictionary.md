# Synthetic Event Data Dictionary

Milestone 2 introduces local-first synthetic event data for the GCP-aligned retail analytics platform. These JSONL files are intentionally small, deterministic, and designed to exercise future publisher, validation, stream processing, dead-letter, replay, and analytics milestones without using cloud services or credentials.

## Event Categories

| Category | File | Purpose |
| --- | --- | --- |
| Customer events | `data/sample/customer_events.jsonl` | Customer lifecycle and preference changes. |
| Product events | `data/sample/product_events.jsonl` | Product discovery, basket, and wishlist interactions. |
| Transaction events | `data/sample/transaction_events.jsonl` | Purchase, payment, and refund outcomes. |
| Session events | `data/sample/session_events.jsonl` | Session lifecycle and checkout journey activity. |

## Shared Fields

| Field | Description |
| --- | --- |
| `event_id` | Stable event identifier used for duplicate detection and idempotency design. |
| `event_type` | Specific business event name within an event category. |
| `event_timestamp` | Time the business event occurred. Future processing will use this as event time. |
| `ingestion_timestamp` | Time the event arrived into the local ingestion boundary. |
| `event_source` | Local synthetic event source namespace. |
| `customer_id` | Stable customer identifier, intentionally malformed for selected edge cases. |
| `session_id` | Stable session identifier, intentionally missing for selected edge cases. |
| `event_version` | Event contract version. |
| `event_category` | One of `customer`, `product`, `transaction`, or `session`. |
| `quality_case` | Marker describing whether a record is normal or an intentional edge case. |

## Category-Specific Fields

Customer events may include:

- `email_domain`
- `loyalty_tier`
- `marketing_channel`

Product events may include:

- `product_id`
- `product_category`
- `unit_price`
- `quantity`

Transaction events may include:

- `transaction_id`
- `order_id`
- `currency`
- `transaction_amount`
- `payment_method`

Session events may include:

- `device_type`
- `traffic_source`
- `page_count`

## Event Types

Customer:

- `customer_registered`
- `customer_logged_in`
- `customer_profile_updated`
- `customer_marketing_opt_in`
- `customer_marketing_opt_out`

Product:

- `product_viewed`
- `product_added_to_basket`
- `product_removed_from_basket`
- `product_wishlisted`

Transaction:

- `purchase_completed`
- `payment_failed`
- `refund_requested`
- `refund_completed`

Session:

- `session_started`
- `session_ended`
- `checkout_started`
- `checkout_abandoned`

## Example Event Records

Customer event:

```json
{
  "event_id": "stable-uuid",
  "event_type": "customer_registered",
  "event_timestamp": "2026-01-15T12:00:00Z",
  "ingestion_timestamp": "2026-01-15T12:00:24Z",
  "event_source": "local.synthetic.customer",
  "customer_id": "cust_00001",
  "session_id": "sess_00001",
  "event_version": "1.0",
  "event_category": "customer",
  "quality_case": "normal",
  "email_domain": "example.com",
  "loyalty_tier": "silver",
  "marketing_channel": "email"
}
```

Transaction event:

```json
{
  "event_id": "stable-uuid",
  "event_type": "purchase_completed",
  "event_timestamp": "2026-01-15T12:00:00Z",
  "ingestion_timestamp": "2026-01-15T12:00:05Z",
  "event_source": "local.synthetic.transaction",
  "customer_id": "cust_00001",
  "session_id": "sess_00001",
  "event_version": "1.0",
  "event_category": "transaction",
  "quality_case": "normal",
  "transaction_id": "txn_000000",
  "order_id": "ord_000000",
  "currency": "GBP",
  "transaction_amount": 42.95,
  "payment_method": "card"
}
```

## Intentional Edge Cases

The sample files include records marked with `quality_case` values that future validation and reliability milestones can route or handle:

| Edge case | Purpose |
| --- | --- |
| `duplicate_event_id` | Tests duplicate detection and idempotent processing. |
| `late_arriving_event` | Tests event-time processing and allowed lateness behavior. |
| `missing_required_field` | Tests schema validation and dead-letter routing. |
| `invalid_timestamp` | Tests timestamp parsing failure handling. |
| `unknown_event_type` | Tests event type allow-list validation. |
| `negative_transaction_amount` | Tests business rule validation. |
| `malformed_customer_id` | Tests identifier format validation. |
| `malformed_product_id` | Tests product identifier format validation. |

## Future Milestone Mapping

- Publisher and consumer milestones can use these JSONL files as local input without Pub/Sub.
- Validation milestones can separate normal records from intentional edge cases.
- Stream processing milestones can use `event_timestamp`, `ingestion_timestamp`, and `event_id` for event-time handling, duplicate detection, idempotency, and dead-letter routing.
- BigQuery-style analytics milestones can model clean customer, product, transaction, and session outputs once invalid records are filtered or isolated.
