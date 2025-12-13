# Logs Directory

This directory contains application logs with automatic rotation.

## Log Files

- **app.log** - Main application log (all levels: DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **error.log** - Error-only log (ERROR and CRITICAL only)

## Configuration

- **Max file size**: 10MB per log file
- **Backup count**: 5 files (keeps last 5 rotated logs)
- **Format**: `timestamp - logger_name - level - message`

## Log Rotation

Logs automatically rotate when they reach 10MB. Old logs are kept with numbered suffixes:
- app.log (current)
- app.log.1 (previous)
- app.log.2 (older)
- ... up to app.log.5

## Usage

Logs are automatically generated when the application runs. To view logs:

```bash
# View latest application logs
tail -f logs/app.log

# View only errors
tail -f logs/error.log

# Search for specific errors
grep "ERROR" logs/app.log

# View last 100 lines
tail -n 100 logs/app.log
```

## Maintenance

Old log files are automatically managed by the rotation system. You can manually clean up if needed:

```bash
# Remove old rotated logs
rm logs/*.log.[1-9]

# Clear all logs (be careful!)
rm logs/*.log
```
