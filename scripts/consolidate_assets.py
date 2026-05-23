import os
import re
import shutil

def main():
    assets_css = 'assets/css'
    vendor = '_vendor'

    print(f"Current working directory: {os.getcwd()}")

    if not os.path.exists(assets_css):
        print(f"Creating {assets_css} directory")
        os.makedirs(assets_css)

    # 1. Consolidate vendor CSS/SCSS
    if os.path.exists(vendor):
        print("Consolidating vendor assets...")
        for root, dirs, files in os.walk(vendor):
            for file in files:
                if file.endswith('.css') or file.endswith('.scss'):
                    src = os.path.join(root, file)
                    # Use .css extension for everything so Tailwind CLI can resolve it
                    target_name = file if file.endswith('.css') else file[:-5] + '.css'
                    dest = os.path.join(assets_css, target_name)

                    # Copy if doesn't exist (to avoid overwriting local files)
                    if not os.path.exists(dest):
                        shutil.copy2(src, dest)
                        # print(f"  Copied {file} -> {target_name}")
    else:
        print(f"Warning: {vendor} directory not found")

    # 2. Add local missing files
    local_files = {
        'generated-theme.css': '/* Placeholder */',
        'tailwind-built.css': '/* Placeholder */'
    }
    for name, content in local_files.items():
        path = os.path.join(assets_css, name)
        if not os.path.exists(path):
            with open(path, 'w') as f:
                f.write(content)

    # 3. Fix main.css imports to use relative paths
    main_css_path = os.path.join(assets_css, 'main.css')
    if os.path.exists(main_css_path):
        print(f"Processing {main_css_path}...")
        with open(main_css_path, 'r') as f:
            content = f.read()

        # This regex looks for @import "something.css" and replaces with @import "./something.css"
        # but only if it doesn't already start with ./ or / or http
        def replace_import(match):
            quote = match.group(1)
            path = match.group(2)
            if path.startswith('./') or path.startswith('/') or path.startswith('http') or path == 'tailwindcss':
                return match.group(0)
            return f'@import {quote}./{path}{quote};'

        new_content = re.sub(r'@import\s+(["\'])([^"\']+)\1\s*;', replace_import, content)

        # Also ensure common missing files are created as empty if they still don't exist
        imports_found = re.findall(r'@import\s+["\']\./([^"\']+)["\']\s*;', new_content)
        for imp in imports_found:
            imp_path = os.path.join(assets_css, imp)
            if not os.path.exists(imp_path):
                print(f"  Creating empty fallback for {imp}")
                with open(imp_path, 'w') as f:
                    f.write(f"/* Fallback for {imp} */\n")

        if content != new_content:
            with open(main_css_path, 'w') as f:
                f.write(new_content)
            print("Successfully updated main.css imports with relative paths.")
        else:
            print("No changes needed in main.css.")
    else:
        print(f"Error: {main_css_path} not found")

if __name__ == "__main__":
    main()
