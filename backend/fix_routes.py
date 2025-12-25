"""
Fix all routes and SQL queries in app.py
"""
import re

with open('app.py', 'r') as f:
    content = f.read()

# Fix all ? to %s in SQL queries (but be careful with string literals)
# Replace in db.execute calls
def fix_sql_queries(text):
    # Pattern 1: Multi-line SQL strings with """
    def fix_multiline(match):
        sql = match.group(1)
        return 'db.execute("""' + sql.replace('?', '%s') + '"""'
    
    text = re.sub(r'db\.execute\("""(.*?)"""', fix_multiline, text, flags=re.DOTALL)
    
    # Pattern 2: Single-line SQL strings
    def fix_singleline(match):
        sql = match.group(1)
        return 'db.execute("' + sql.replace('?', '%s') + '"'
    
    text = re.sub(r'db\.execute\("([^"]*)"', fix_singleline, text)
    
    return text

content = fix_sql_queries(content)

# Fix redirects
content = content.replace('redirect("/")', 'redirect("/df/")')
content = content.replace('redirect("/admin', 'redirect("/df/admin')
content = content.replace('redirect("/login")', 'redirect("/df/login")')
content = content.replace('redirect("/upload")', 'redirect("/df/upload")')

# Fix route decorators
content = content.replace('@app.route("/', '@app.route("/df/')
content = content.replace('@app.route(\"/', '@app.route("/df/')

# Fix info and history routes
content = content.replace('@app.route("/df/df/', '@app.route("/df/')

with open('app.py', 'w') as f:
    f.write(content)

print("Fixed routes and SQL queries")

