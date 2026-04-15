# Contributing to Bus Ticket Booking System

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Code of Conduct

- Be respectful and inclusive
- Report issues responsibly
- Focus on the code, not the person

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR-USERNAME/Bus-Ticket-Booking-System.git`
3. Add upstream remote: `git remote add upstream https://github.com/Puneetdivedi/Bus-Ticket-Booking-System.git`
4. Create a branch: `git checkout -b feature/your-feature-name`

## Development Workflow

### Setup

Follow the [DEVELOPMENT.md](DEVELOPMENT.md) guide to setup your local environment.

### Making Changes

1. Create a descriptive branch name:
   - `feature/add-new-endpoint` for new features
   - `fix/issue-title` for bug fixes
   - `docs/update-readme` for documentation
   - `refactor/component-name` for refactoring

2. Make focused commits:
   ```bash
   git commit -m "fix: resolve booking conflict detection bug"
   ```

3. Use conventional commit format:
   - `feat:` - New feature
   - `fix:` - Bug fix
   - `docs:` - Documentation
   - `style:` - Code style (formatting, semicolons, etc)
   - `refactor:` - Code refactoring
   - `perf:` - Performance improvement
   - `test:` - Adding tests

### Code Quality

Before submitting:

```bash
# Backend
cd backend
black app/
flake8 app/
mypy app/
pytest

# Frontend
cd frontend
npm run lint
npm run format
npm test
```

### Testing

- Write tests for new features
- Ensure all tests pass: `pytest` or `npm test`
- Target >80% code coverage for new code

### Documentation

- Update README.md for user-facing changes
- Update DEVELOPMENT.md for technical changes
- Add docstrings to functions
- Include examples in comments

## Pull Request Process

1. **Update main branch**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Push your branch**
   ```bash
   git push origin your-feature-branch
   ```

3. **Create Pull Request**
   - Use descriptive title
   - Reference related issues: `Fixes #123`
   - Include what changed and why

4. **PR Template**
   ```markdown
   ## Description
   Brief description of changes

   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update

   ## Related Issues
   Fixes #123

   ## How to Test
   Steps to test the changes

   ## Screenshots (if applicable)
   Screenshots or GIFs

   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Tests added/updated
   - [ ] Documentation updated
   - [ ] No new warnings generated
   ```

5. **Review Process**
   - Address review comments
   - Push updates to the same branch
   - Request re-review after changes

## Reporting Issues

### Bug Reports

Include:
- Clear title describing the issue
- Steps to reproduce
- Expected behavior
- Actual behavior
- Screenshots/logs
- Environment (OS, Python version, browser, etc)

Template:
```markdown
## Description
Brief description of the bug

## Steps to Reproduce
1. Navigate to...
2. Click on...
3. See error...

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Screenshots
If applicable

## Environment
- OS: Windows/macOS/Linux
- Browser: Chrome/Firefox/Safari
- Python: 3.10/3.11/3.12
- Node: 18/20
```

### Feature Requests

Include:
- Use case and motivation
- Proposed solution
- Alternative solutions
- Additional context

## Documentation Guidelines

- Use clear, concise language
- Include code examples
- Keep documentation up-to-date
- Link related sections

## Review Guidelines

When reviewing PRs:

1. **Code Quality**
   - Does it follow project standards?
   - Is it well-documented?
   - Are edge cases handled?

2. **Testing**
   - Are there adequate tests?
   - Do tests cover edge cases?
   - Do all tests pass?

3. **Performance**
   - Are there any performance concerns?
   - Are database queries optimized?

4. **Security**
   - Are there any security vulnerabilities?
   - Is input validation present?
   - Are secrets properly handled?

5. **Backwards Compatibility**
   - Does it break existing functionality?
   - Are migrations needed?

## Project Structure

```
.
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── api/         # API routes
│   │   ├── services/    # Business logic
│   │   └── models.py    # Database models
│   └── requirements.txt
├── frontend/             # React application
│   ├── src/
│   │   ├── components/  # React components
│   │   └── api/         # API client
│   └── package.json
├── database/             # Database files and schemas
├── README.md
└── DEVELOPMENT.md
```

## Performance Considerations

- Optimize database queries
- Implement pagination for large datasets
- Use caching where appropriate
- Profile code for bottlenecks

## Security Considerations

- Never commit secrets or API keys
- Validate all user input
- Use parameterized queries
- Implement proper authentication/authorization
- Keep dependencies updated

## Version Control

- Use `git rebase` for local branch cleanup
- Write clear commit messages
- Keep commits atomic and logical
- Don't force push to shared branches

## Deployment

- Changes to main branch trigger CI/CD
- All tests must pass before merge
- Manual review required for sensitive changes
- Deployment to staging for verification
- Production deployment after sign-off

## Communication

- Use GitHub Issues for discussions
- Tag maintainers with @mention when needed
- Join our Discord for real-time chat
- Email: support@yourdomain.com

## Licensing

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

- Check existing issues
- Read documentation
- Ask in GitHub Discussions
- Email the maintainers

---

Thank you for contributing! 🙏
