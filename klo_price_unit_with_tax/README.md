# KLO - Price Unit with Tax in Sale Order Lines

## Description

This module adds a new field `price_unit_with_tax` to the sale order lines (`sale.order.line`) that automatically calculates and displays the unit price with taxes included.

## Features

- Adds a new computed and stored field `price_unit_with_tax` in sale order lines
- The field is displayed next to the standard `price_unit` field in both tree and form views
- Automatically calculates the unit price including all applicable taxes
- Updates automatically when price, quantity, discount, or taxes change

## Installation

1. Copy this module to your Odoo addons directory
2. Update the apps list
3. Install the module from Apps menu

## Usage

Once installed, you will see a new column "Unit Price with Tax" in your sale order lines, right after the "Unit Price" column. This field will automatically display the unit price with taxes included.

## Technical Information

- **Version**: 18.0.1.0.0
- **Category**: Sales/Sales
- **Depends**: sale
- **License**: AGPL-3

## Author

KLO Ingeniería Informática S.L.L.
- Website: https://www.klo.es

## Copyright

Copyright 2026 KLO Ingeniería Informática S.L.L.

