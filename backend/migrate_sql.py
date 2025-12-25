"""
Script to convert SQLite queries to PostgreSQL format
Replaces ? with %s in SQL queries
"""
import re
import sys

def convert_sql_file(filename):
    with open(filename, 'r') as f:
        content = f.read()
    
    # Replace ? with %s in SQL queries (but not in Python code)
    # Pattern: Look for SQL strings in execute() calls
    patterns = [
        (r'db\.execute\("([^"]*)\?",', r'db.execute("\1%s",'),
        (r'db\.execute\("""([^"]*)\?"""', r'db.execute("""\1%s"""'),
        (r'db\.execute\("""([^"]*)\?"""', r'db.execute("""\1%s"""'),
        (r'WHERE.*= \?', lambda m: m.group(0).replace('?', '%s')),
        (r'VALUES \(.*\?', lambda m: m.group(0).replace('?', '%s')),
    ]
    
    # Simple replacement: ? -> %s in SQL context
    # More careful: replace ? with %s only in SQL strings
    lines = content.split('\n')
    new_lines = []
    in_sql_string = False
    
    for line in lines:
        # Check if we're in a multi-line SQL string
        if '"""' in line or "'''" in line:
            in_sql_string = not in_sql_string
        
        # Replace ? with %s in SQL execute calls
        if 'db.execute' in line or in_sql_string:
            # Count quotes to see if we're in a string
            single_quotes = line.count("'") - line.count("\\'")
            double_quotes = line.count('"') - line.count('\\"')
            if single_quotes % 2 == 0 and double_quotes % 2 == 0:
                # Replace ? with %s but preserve escaped quotes
                line = re.sub(r'\?', '%s', line)
        
        new_lines.append(line)
    
    return '\n'.join(new_lines)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        converted = convert_sql_file(filename)
        with open(filename, 'w') as f:
            f.write(converted)
        print(f"Converted {filename}")
    else:
        print("Usage: python migrate_sql.py <filename>")

