#!/bin/bash

# Export all relevant code files to a single text file
OUTPUT="code_export.txt"

echo "=== STORE PROJECT CODE EXPORT ===" > $OUTPUT
echo "Generated: $(date)" >> $OUTPUT
echo "" >> $OUTPUT

# Function to add file with header
add_file() {
    if [ -f "$1" ]; then
        echo "================================================" >> $OUTPUT
        echo "FILE: $1" >> $OUTPUT
        echo "================================================" >> $OUTPUT
        cat "$1" >> $OUTPUT
        echo "" >> $OUTPUT
        echo "" >> $OUTPUT
    fi
}

# Backend - Django
echo "### BACKEND ###" >> $OUTPUT
add_file "backend/config/settings/base.py"
add_file "backend/config/settings/production.py"
add_file "backend/config/urls.py"
add_file "backend/apps/catalog/models.py"
add_file "backend/apps/catalog/views.py"
add_file "backend/apps/catalog/serializers.py"
add_file "backend/apps/catalog/urls.py"
add_file "backend/apps/catalog/admin.py"
add_file "backend/apps/orders/models.py"
add_file "backend/apps/orders/views.py"
add_file "backend/apps/orders/serializers.py"
add_file "backend/apps/orders/urls.py"
add_file "backend/apps/payments/views.py"
add_file "backend/apps/payments/urls.py"
add_file "backend/requirements.txt"
add_file "backend/Procfile"
add_file "backend/railway.toml"

# Frontend - Next.js
echo "### FRONTEND ###" >> $OUTPUT
add_file "frontend/src/lib/api.ts"
add_file "frontend/src/types/index.ts"
add_file "frontend/src/app/layout.tsx"
add_file "frontend/src/app/page.tsx"
add_file "frontend/src/app/collections/page.tsx"
add_file "frontend/src/app/collections/[slug]/page.tsx"
add_file "frontend/src/app/photos/page.tsx"
add_file "frontend/src/app/photos/[slug]/page.tsx"
add_file "frontend/src/app/cart/page.tsx"
add_file "frontend/src/app/checkout/success/page.tsx"
add_file "frontend/src/components/PhotoCard.tsx"
add_file "frontend/src/components/Header.tsx"
add_file "frontend/src/components/Footer.tsx"
add_file "frontend/src/components/CartProvider.tsx"
add_file "frontend/package.json"
add_file "frontend/netlify.toml"
add_file "frontend/next.config.ts"
add_file "frontend/tsconfig.json"

# Root config
echo "### ROOT CONFIG ###" >> $OUTPUT
add_file ".gitignore"

echo "Export complete: $OUTPUT"
echo "Lines: $(wc -l < $OUTPUT)"
