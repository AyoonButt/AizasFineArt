# Claude Instructions for Aiza's Fine Art Project

This file contains instructions that should be read by Claude in every session to maintain consistency and comprehensive logging.

## 🚨 MANDATORY SESSION STARTUP CHECKLIST

Every Claude session MUST start by following these steps:

### 1. Read Project Context
- [ ] Read `CLAUDE.md` for comprehensive project history
- [ ] Review the most recent session log in `logs/sessions/`
- [ ] Check `logs/decisions/` for recent technical decisions
- [ ] Review any error logs in `logs/errors/` to avoid repeating issues

### 2. Create Session Log
- [ ] Create new session log file: `logs/sessions/session_YYYYMMDD_HHMMSS_[ID].log`
- [ ] Document session start time, context, and goals
- [ ] Note any continuing work from previous sessions

### 3. System Prompt Awareness
- [ ] Acknowledge this is for **Aiza's Fine Art Website**
- [ ] Remember the comprehensive system prompt specifications (if provided in conversation)
- [ ] Note: Artist bio, color palette, typography, and technical requirements

## 📝 MANDATORY LOGGING REQUIREMENTS

### For Every Significant Action:
1. **Before Acting**: Document decision reasoning
2. **During Action**: Note specific steps taken
3. **After Action**: Record results and any issues

### Log Entry Template for CLAUDE.md:
```markdown
## [TIMESTAMP] - [SESSION_ID] - [ACTION_TYPE]
**Context**: What were you working on
**Decision**: What you decided to do and why
**Actions Taken**: 
- Specific action 1
- Specific action 2
**Files Modified**: List all files changed
**Reasoning**: Technical reasoning
**Impact**: How this affects the project
**Next Steps**: What should be done next
---
```

### Action Types to Use:
- **SETUP**: Project configuration and environment
- **FEATURE**: New functionality implementation  
- **BUG_FIX**: Fixing issues and errors
- **REFACTOR**: Code improvements and reorganization
- **CLEANUP**: Code cleanup and maintenance
- **DOCUMENTATION**: Documentation updates
- **TESTING**: Test implementation and fixes
- **DEPLOYMENT**: Deployment-related changes
- **ARCHITECTURE**: Major technical decisions

## 🎯 PROJECT SPECIFIC GUIDELINES

### Technology Stack Requirements:
- **Backend**: Django 4.2+ with Django REST Framework
- **Database**: Supabase PostgreSQL (dev: SQLite)
- **Frontend**: Django templates + React components
- **Styling**: Tailwind CSS with custom design system
- **Animations**: GSAP for organic animations

### Color Palette (Warm Earth Tones):
- **Primary**: #A67C52 (Mocha Mousse)
- **Secondary**: #A78BFA (Digital Lavender)  
- **Neutral**: #FFFFFF (Crisp White)
- **Accent**: #E2725B (Terracotta Red)

### Typography (Classic Elegance):
- **Headlines**: Playfair Display
- **Body**: DM Sans
- **Accents**: League Spartan

### Key Features to Remember:
- **Artist**: Aiza, Fort Worth TX, watercolor/oil paintings
- **Business Model**: Original art sales + Lumaprints integration
- **Design**: Professional gallery quality with authentic personality
- **SEO**: URL structure `/art/[category]/[artwork-slug]/`

## 🔄 SESSION HANDOFF PROTOCOL

### When Ending a Session:
1. **Update CLAUDE.md** with final session entry
2. **Complete session log** with end time and status
3. **Document next steps** clearly for following session
4. **Note any incomplete work** or pending decisions

### When Starting a New Session:
1. **Read all mandatory files** listed above
2. **Review incomplete work** from previous session
3. **Confirm understanding** of current project state
4. **Plan session approach** based on context

## ⚠️ CRITICAL REMINDERS

- **NEVER** skip logging - every significant action must be documented
- **ALWAYS** read previous logs before making decisions
- **MAINTAIN** consistency with established patterns
- **PRESERVE** system prompt specifications in all implementations
- **DOCUMENT** reasoning behind all technical decisions

## 📞 EMERGENCY PROTOCOLS

If you encounter:
- **Conflicting instructions**: Document the conflict and ask for clarification
- **Major errors**: Log in `logs/errors/` with full context and attempted solutions
- **Architectural questions**: Document options in `logs/decisions/` before choosing

This logging system ensures continuity across all Claude sessions and provides developers with complete context for understanding AI decisions and actions.