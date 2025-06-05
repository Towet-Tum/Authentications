# Authentications

# Run black
black .

# Remove unused imports
autoflake --in-place --remove-unused-variables --remove-all-unused-imports -r .

# Fix whitespace and minor issues
autopep8 --in-place --aggressive --aggressive -r .
 autopep8 . --in-place --recursive --max-line-length 79


# Final check
flake8
