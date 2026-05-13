# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.20] - 2026-05-13

### Added

- `stream/v1` WebSocket client (`stream_v1` package, models, auth, public, subscription).
- `account.read_notifications()` method — maps to `PUT /account/notifications` (mark all as read).
- `examples/stream_v1.py` demonstrating WebSocket usage.

### Changed

- Package layout: `lnmarkets_sdk.rest_v3` → `lnmarkets_sdk.rest.v3`.
- Renamed `examples/basic.py` → `examples/rest_v3.py`.
- `examples/rest_v3.py`: take-profit update now opens a real isolated market trade and uses its ID instead of hardcoded UUID.

### Removed

- `AccountClient.withdraw_internal` (endpoint not present in api-rest-v3).
- `AccountClient.get_internal_deposits` (endpoint not present in api-rest-v3).
- `AccountClient.get_internal_withdrawals` (endpoint not present in api-rest-v3).
- Associated models: `WithdrawInternalParams`, `WithdrawInternalResponse`, `InternalDeposit`, `InternalWithdrawal`, `GetInternalDepositsParams`, `GetInternalWithdrawalsParams`.

### Fixed

- `examples/rest_v3.py`: `update_takeprofit` no longer hits hardcoded trade ID that returned `400 You do not own this trade`.
