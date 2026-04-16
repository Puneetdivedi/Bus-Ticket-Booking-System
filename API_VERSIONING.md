# API Versioning Strategy

## Version Format

Uses semantic versioning: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking API changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, no API changes

## Current Version

- **API Version**: 1.1.0
- **Release Date**: April 16, 2026
- **Status**: Active

## Version History

### v1.1.0 (April 16, 2026)
**New Features:**
- Added `/api/info` endpoint with detailed API information
- Improved health check with version information
- Added comprehensive test suite
- Added request utilities for ID generation
- Added decorators for request context management
- Updated API tags and documentation

**Improvements:**
- Better error handling and validation
- Structured error responses
- Enhanced logging capabilities
- Added request tracing with request IDs

**Backward Compatible:** Yes

### v1.0.0 (April 15, 2026)
**Initial Release:**
- Basic booking management APIs
- Boarding sequence optimization
- Seat availability checking
- CSV export functionality
- Mobile search support
- Authentication support

## Upgrade Path

### From v1.0.0 to v1.1.0

No breaking changes. All existing endpoints continue to work:
- Existing API calls remain compatible
- New endpoints are additive only
- Database schema is unchanged
- No migration needed

## Future Versions

### v2.0.0 (Planned)
- GraphQL API support
- Real-time updates with WebSockets
- Advanced analytics endpoints
- Multi-language support
- Rate limiting enhancements

## Deprecation Policy

Features will be marked as deprecated with:
- Clear deprecation warnings in logs
- Support for 2+ versions
- Migration guide for replacements
- Timeline for removal

## Version Detection

Check API version:
```bash
curl http://localhost:8000/api/info
```

Or check health:
```bash
curl http://localhost:8000/api/health
```

## Release Schedule

- **Patch releases**: As needed for bug fixes
- **Minor releases**: Quarterly for new features
- **Major releases**: Annually or when breaking changes are necessary
