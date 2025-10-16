# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-01-16

### Added
- Initial release of Pulseway MCP Server
- Model Context Protocol (MCP) server implementation
- Integration with Pulseway RMM API
- Support for uv package manager
- Token-based authentication with Pulseway API
- Core tools:
  - `list_systems` - List all managed systems
  - `get_system_details` - Get detailed system information
  - `get_system_notifications` - Retrieve system notifications
  - `list_organizations` - List all organizations
  - `get_system_metrics` - Get performance metrics
- MCP resources:
  - `pulseway://docs/api` - API documentation
  - `pulseway://systems` - System list
- Comprehensive test suite with pytest
- Type checking with mypy
- Code formatting with ruff
- GitHub Actions CI/CD pipeline
- Documentation:
  - README with installation and usage instructions
  - CONTRIBUTING guide
  - Example configuration files

### Security
- Secure token-based authentication
- Environment variable configuration
- No credentials in code

[Unreleased]: https://github.com/yourusername/pulseway-mcp-server/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/yourusername/pulseway-mcp-server/releases/tag/v0.1.0
