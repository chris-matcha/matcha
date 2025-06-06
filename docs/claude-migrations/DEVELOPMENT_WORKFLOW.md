# Matcha Development Workflow

## 🔧 Change Management Process

### 1. Before Making Changes
```bash
# Always start from main branch
git checkout main
git pull origin main

# Create a feature branch for each issue
git checkout -b fix/specific-issue-name
```

### 2. One Issue Per Branch
- **PDF text replacement** → `fix/pdf-text-replacement`
- **Translation downloads** → `fix/translation-downloads`  
- **Filename prefixes** → `fix/filename-prefixes`

### 3. Testing Protocol
Before committing any changes:
1. Test with a simple PDF (2-3 pages)
2. Try all three profiles (Dyslexia, ADHD, ESL)
3. Test with and without translation
4. Verify download functionality

### 4. Commit Strategy
```bash
# Small, focused commits
git add specific_file.py
git commit -m "Fix: specific issue description

- What was broken
- How it was fixed
- What to test"
```

### 5. Rollback Strategy
```bash
# Revert last commit
git revert HEAD

# Go back to specific commit
git reset --hard <commit-hash>

# Restore specific file
git restore app.py
```

## 🎯 Current Issue Priorities

1. **High Priority**: PDF text replacement (original text still visible)
2. **Medium Priority**: Translation downloads not appearing
3. **Low Priority**: Text positioning improvements

## 🧪 Test Cases

### Basic Functionality Test
- [ ] Upload PDF
- [ ] Select Dyslexia profile
- [ ] Click "Direct Adaptation" 
- [ ] Download works
- [ ] Adapted text replaces original

### Translation Test
- [ ] Upload PDF
- [ ] Select any profile + language
- [ ] Both files appear for download
- [ ] Translation file contains translated content

### Regression Test
- [ ] PowerPoint adaptation still works
- [ ] Assessment mode still works
- [ ] All three profiles work

## 🔍 Debug Commands

```bash
# Check what files were created
ls -la outputs/ | grep "$(date +%Y-%m-%d)"

# Monitor server logs
tail -f app.log

# Check git changes
git diff --name-only
```