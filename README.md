# AMBER CAST — Handcrafted Artisanal Brass & Metalcraft Atelier

A luxury e-commerce and foundry inventory management web platform built using **Python Django**, designed for purchasing, curating, and governing handcrafted solid brass metalwork, sacred statues, traditional oil lamps, and architectural fittings.

---

## ✨ Features Overview

### 🛍️ Collector Storefront & Commerce
- **Grand Hero Showcase**: Highlights canonical Chola lost-wax masterworks (*Nataraja 18"*, *Venugopala Krishna*, *Ganesha on Lotus Throne*).
- **Artisanal Product Catalog**:
  - Filter by category (*Temple Deities*, *Ritual Diyas & Deepams*, *Water Urulis & Bowls*, *Resonant Ghanta Bells*, *Luminaires*, *Cabinetry*, *Timepieces*).
  - Filter by surface patina (*Antique Brown*, *Polished Gold*, *Smoked Matte Bronze*).
  - Price valuation slider & instant keyword search across title, description, and metallurgy alloy.
  - Interactive **Quick Inspect Drawer** with metallurgical parameters, mass in kg, dimensions, and instant cart reservation.
- **Dedicated Product Inspection**: High-resolution gallery angles, full Shilpa Shastras iconography specifications, stock counter, and verified collector reviews.
- **Atelier Curation Bag & Vault Checkout**:
  - Live quantity modification (`+` / `-`) and subtotal calculations.
  - Stored dossier address quick-select (Primary Residence vs Design Studio).
  - Two-tier settlement: **Instant Digital Escrow** (UPI / Card / Net Banking) or **Cash On Delivery (COD)** upon unboxing inspection.
  - Patron privilege voucher token (`AMBER10` gives 10% discount).
  - Serialized **Guild Commission Certificate & Vault Receipt** with print support.
- **Patron Orders Ledger & Production Timeline**: 4-stage tracking (*Smelt Pour* &rarr; *Hand Chasing* &rarr; *Armored Transit* &rarr; *Vault Received*).
- **Collector Appraisals & Testimonials**: 5-star evaluation system and review submission.
- **The Cire-Perdue Heritage Chronicle**: Deep-dive narrative into the 5,000-year-old lost-wax casting technique.

---

### 🏛️ Atelier Workshop Console (Admin Dashboard)
- **Bento Metrology Metrics**: Gross Guild Revenue ($184k+), Active Commissions, Low Stock alerts, and Curated Patron metrics with visual sparklines.
- **Artisan Ingot Inventory Governance**:
  - Real-time SKU search and category filtering.
  - Live unit price, remaining casting stock, and availability state tags.
  - Instant `+5 Smelt` quick restock button with real-time stock feedback.
- **Furnace Smelting Balance & Telemetry**: Crucible raw material monitoring (*Alloy 85/15 Red Brass*, *Natural Amber Resin*, *Silicon Bronze*) and furnace induction temperature logging (1,150°C).
- **Order Commission & Fulfillment Stream**:
  - Live order tracker with patron contact, date, total, and settlement state.
  - Instant fulfillment status updater dropdown (*Processing*, *Shipped*, *Delivered*, *Cancelled*).
  - Guild commission certificate inspection and printing.
- **Mint New Brass Casting**: Interactive modal with real-time live preview rendering for publishing new artworks to the catalog.
- **Fiscal Analytics & Sub-consoles**: Dedicated pages for Orders Fulfillment, Catalog Management, and Sales Analytics.

---

## 🗄️ Database Architecture (SRS Compliant)

| Model | Table Name | Key Attributes |
|---|---|---|
| **User** | `store_user` | `id`, `email` (unique), `first_name`, `last_name`, `phone`, `address`, `role` ('Customer'/'Admin') |
| **Product** | `store_product` | `id`, `sku`, `product_name`, `category`, `price`, `stock_quantity`, `weight`, `dimensions`, `alloy_blend`, `patina_finish` |
| **ProductImage** | `store_productimage` | `id`, `product_id`, `image_path`, `is_primary` |
| **Cart** | `store_cart` | `id`, `user_id` (1:1), `created_at` |
| **CartItem** | `store_cartitem` | `id`, `cart_id`, `product_id`, `quantity`, `unit_price`, `subtotal` |
| **Order** | `store_order` | `id`, `order_reference` (`#ORD-...`), `user_id`, `total_amount`, `shipping_address`, `payment_status`, `order_status` |
| **OrderItem** | `store_orderitem` | `id`, `order_id`, `product_id`, `quantity`, `unit_price`, `subtotal` |
| **Payment** | `store_payment` | `id`, `order_id` (1:1), `payment_method`, `transaction_id`, `amount`, `payment_status`, `payment_date` |
| **Inventory** | `store_inventory` | `id`, `product_id` (1:1), `quantity_available`, `last_updated` |
| **Review** | `store_review` | `id`, `user_id`, `product_id`, `rating` (1-5), `comment`, `created_at` |

---

## 🚀 Setup & Execution Guide

### 1. Requirements
Ensure you have Python 3.10+ installed on your machine.

### 2. Install Dependencies
```bash
pip install django pillow
```

### 3. Apply Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Seed Database with Artisanal Brass Art & Sample Orders
```bash
python manage.py seed_data
```
*Seeds 14 authentic handcrafted brass pieces with photography, inventory records, default user accounts, active cart, reviews, and test orders.*

### 5. Launch Local Server
```bash
python manage.py runserver
```
Visit **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your browser.

---

## 🔑 Default Test Credentials

| Account Role | Email | Password | Access URL |
|---|---|---|---|
| **Guild Administrator** | `admin@ambercast.com` | `admin123` | `/atelier/` or `/admin/` |
| **Collector / Patron** | `devraj@heritage.com` | `customer123` | `/login/` or `/cart/` |

> 💡 **Patron Privilege Token**: Enter voucher code `AMBER10` during checkout to receive an instant 10% privilege discount.
