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

# ============================================
# BACKEND - Django
# ============================================
echo "### BACKEND ###" >> $OUTPUT

# Config/Settings
add_file "backend/config/settings/base.py"
add_file "backend/config/settings/production.py"
add_file "backend/config/urls.py"
add_file "backend/config/celery.py"
add_file "backend/requirements.txt"
add_file "backend/Procfile"
add_file "backend/start.sh"

# Catalog App (Photos, Collections, Products)
add_file "backend/apps/catalog/models.py"
add_file "backend/apps/catalog/views.py"
add_file "backend/apps/catalog/serializers.py"
add_file "backend/apps/catalog/urls.py"
add_file "backend/apps/catalog/admin.py"
add_file "backend/apps/catalog/management/commands/generate_photo_descriptions.py"
add_file "backend/apps/catalog/management/commands/generate_photo_embeddings.py"
add_file "backend/apps/catalog/management/commands/find_orphan_files.py"

# Orders App (Cart, Orders)
add_file "backend/apps/orders/models.py"
add_file "backend/apps/orders/views.py"
add_file "backend/apps/orders/serializers.py"
add_file "backend/apps/orders/urls.py"
add_file "backend/apps/orders/admin.py"

# Payments App (Stripe)
add_file "backend/apps/payments/views.py"
add_file "backend/apps/payments/urls.py"

# Core App (Contact, Newsletter, Gift Cards)
add_file "backend/apps/core/models.py"
add_file "backend/apps/core/views.py"
add_file "backend/apps/core/serializers.py"
add_file "backend/apps/core/urls.py"
add_file "backend/apps/core/admin.py"
add_file "backend/apps/core/emails.py"

# Chat App (AI Shopping Agent - LangChain)
add_file "backend/apps/chat/models.py"
add_file "backend/apps/chat/views.py"
add_file "backend/apps/chat/urls.py"
add_file "backend/apps/chat/admin.py"
add_file "backend/apps/chat/agent.py"
add_file "backend/apps/chat/tools.py"
add_file "backend/apps/chat/prompts.py"

# Mockup App (ML Wall Detection)
add_file "backend/apps/mockup/models.py"
add_file "backend/apps/mockup/views.py"
add_file "backend/apps/mockup/serializers.py"
add_file "backend/apps/mockup/urls.py"
add_file "backend/apps/mockup/admin.py"
add_file "backend/apps/mockup/tasks.py"
add_file "backend/apps/mockup/wall_detection.py"
add_file "backend/apps/mockup/depth_estimation.py"

# ============================================
# FRONTEND - Next.js
# ============================================
echo "### FRONTEND ###" >> $OUTPUT

# Config
add_file "frontend/package.json"
add_file "frontend/next.config.ts"
add_file "frontend/tsconfig.json"
add_file "frontend/netlify.toml"
add_file "frontend/tailwind.config.ts"

# Core/Lib
add_file "frontend/src/lib/api.ts"
add_file "frontend/src/types/index.ts"

# App Layout & Root Pages
add_file "frontend/src/app/layout.tsx"
add_file "frontend/src/app/page.tsx"

# Collections Pages
add_file "frontend/src/app/collections/page.tsx"
add_file "frontend/src/app/collections/[slug]/page.tsx"

# Photos Pages
add_file "frontend/src/app/photos/page.tsx"
add_file "frontend/src/app/photos/[slug]/page.tsx"

# Cart & Checkout
add_file "frontend/src/app/cart/page.tsx"
add_file "frontend/src/app/checkout/success/page.tsx"

# Book/Products
add_file "frontend/src/app/book/page.tsx"

# Gift Cards
add_file "frontend/src/app/gift-cards/page.tsx"

# Contact & About
add_file "frontend/src/app/contact/page.tsx"
add_file "frontend/src/app/about/page.tsx"

# Order Tracking
add_file "frontend/src/app/track-order/page.tsx"
add_file "frontend/src/app/order/[orderNumber]/page.tsx"

# Shipping Info
add_file "frontend/src/app/shipping/page.tsx"

# Core Components
add_file "frontend/src/components/Header.tsx"
add_file "frontend/src/components/Footer.tsx"
add_file "frontend/src/components/PhotoCard.tsx"
add_file "frontend/src/components/CartProvider.tsx"
add_file "frontend/src/components/AddToCartButton.tsx"
add_file "frontend/src/components/CropOverlay.tsx"
add_file "frontend/src/components/PhotoGrid.tsx"

# Chat Components (AI Shopping Agent)
add_file "frontend/src/components/chat/ChatWidget.tsx"
add_file "frontend/src/components/chat/ChatWindow.tsx"
add_file "frontend/src/components/chat/ChatMessage.tsx"
add_file "frontend/src/components/chat/ChatInput.tsx"

# Mockup Components (Room Visualization)
add_file "frontend/src/components/mockup/MockupTool.tsx"
add_file "frontend/src/components/mockup/RoomUploader.tsx"
add_file "frontend/src/components/mockup/WallCanvas.tsx"
add_file "frontend/src/components/mockup/PrintPreview.tsx"

# ============================================
# ROOT CONFIG
# ============================================
echo "### ROOT CONFIG ###" >> $OUTPUT
add_file "CLAUDE.md"
add_file "docker-compose.yml"

echo "Export complete: $OUTPUT"
echo "Lines: $(wc -l < $OUTPUT)"
