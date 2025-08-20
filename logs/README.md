# Claude Development Logs

This directory contains comprehensive logs of all Claude/AI agent activities on this codebase.

## Directory Structure

### `/sessions/`
Contains session-specific logs with timestamps and context
- Each session gets a unique ID and log file
- Tracks start/end times, context switches, and session goals

### `/decisions/`
Contains detailed decision logs with reasoning
- Technical architecture decisions
- Implementation approach choices
- Trade-off analyses and rationale

### `/actions/`
Contains granular action logs
- File modifications with diffs
- Command executions
- API calls and responses

### `/errors/`
Contains error logs and resolution attempts
- Compilation errors and fixes
- Runtime errors and debugging
- Failed attempts and lessons learned

## Log File Naming Convention

- Sessions: `session_YYYYMMDD_HHMMSS_[SESSION_ID].log`
- Decisions: `decision_YYYYMMDD_HHMMSS_[TOPIC].log`
- Actions: `action_YYYYMMDD_HHMMSS_[ACTION_TYPE].log`
- Errors: `error_YYYYMMDD_HHMMSS_[ERROR_TYPE].log`

## Usage

1. **For Developers**: Review logs to understand AI decision-making process
2. **For Claude/Agents**: Append to logs for each significant action
3. **For Debugging**: Trace back through decision and action history
4. **For Handoffs**: Provide context when switching between different AI agents

## Integration

- All Claude sessions should start by reading recent logs for context
- Major decisions should be documented with full reasoning
- Actions should include before/after states when relevant
- Errors should include attempted solutions and final resolution