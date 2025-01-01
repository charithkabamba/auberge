# Generated by Django 5.0.8 on 2024-12-08 07:20

import django.db.models.deletion
import django_extensions.db.fields
import products.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("categories", "0002_alter_category_options"),
    ]

    operations = [
        migrations.CreateModel(
            name="Product",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    django_extensions.db.fields.CreationDateTimeField(
                        auto_now_add=True, verbose_name="created"
                    ),
                ),
                (
                    "modified",
                    django_extensions.db.fields.ModificationDateTimeField(
                        auto_now=True, verbose_name="modified"
                    ),
                ),
                ("name", models.CharField(max_length=255, verbose_name="Product name")),
                ("description", models.TextField(help_text="Main product description")),
                (
                    "additional_details",
                    models.TextField(
                        blank=True, help_text="Additional details about the product"
                    ),
                ),
                (
                    "original_price",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                ("selling_price", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Whether the product is available for sale",
                    ),
                ),
                ("brand", models.CharField(blank=True, max_length=200, null=True)),
                (
                    "stock",
                    models.IntegerField(
                        help_text="Available quantity in stock", verbose_name="Stock"
                    ),
                ),
                (
                    "stock_unit",
                    models.IntegerField(
                        choices=[
                            (1, "kg"),
                            (2, "gm"),
                            (3, "ltr"),
                            (4, "ml"),
                            (5, "unit"),
                        ],
                        help_text="Unit of measurement for the stock",
                    ),
                ),
                (
                    "minimum_stock",
                    models.IntegerField(
                        default=0, help_text="Minimum stock level before reorder"
                    ),
                ),
                (
                    "top_featured",
                    models.BooleanField(
                        default=False, help_text="Whether the product is featured"
                    ),
                ),
                (
                    "sku",
                    models.CharField(
                        help_text="Stock Keeping Unit", max_length=50, unique=True
                    ),
                ),
                (
                    "barcode",
                    models.CharField(
                        blank=True,
                        help_text="Product barcode (ISBN, UPC, etc.)",
                        max_length=50,
                        null=True,
                    ),
                ),
                (
                    "slug",
                    models.SlugField(
                        help_text="URL-friendly version of the product name",
                        unique=True,
                    ),
                ),
                (
                    "meta_keywords",
                    models.CharField(
                        blank=True,
                        help_text="Comma-separated keywords for SEO",
                        max_length=255,
                        null=True,
                        verbose_name="Meta Keywords",
                    ),
                ),
                (
                    "meta_description",
                    models.CharField(
                        blank=True,
                        help_text="Short description for SEO",
                        max_length=255,
                        null=True,
                        verbose_name="Meta Description",
                    ),
                ),
                (
                    "weight",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        help_text="Product weight for shipping calculations",
                        max_digits=10,
                        null=True,
                    ),
                ),
                (
                    "is_free_shipping",
                    models.BooleanField(
                        default=False, help_text="Whether the product ships free"
                    ),
                ),
                (
                    "has_variants",
                    models.BooleanField(
                        default=False,
                        help_text="Whether this product has different variants",
                    ),
                ),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="categories.category",
                    ),
                ),
            ],
            options={
                "verbose_name": "Product",
                "verbose_name_plural": "Products",
                "ordering": ["-created"],
            },
        ),
        migrations.CreateModel(
            name="ProductImage",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    django_extensions.db.fields.CreationDateTimeField(
                        auto_now_add=True, verbose_name="created"
                    ),
                ),
                (
                    "modified",
                    django_extensions.db.fields.ModificationDateTimeField(
                        auto_now=True, verbose_name="modified"
                    ),
                ),
                (
                    "image",
                    models.ImageField(
                        upload_to=products.models.product_image_directory_path,
                        verbose_name="Product Image",
                    ),
                ),
                ("is_primary", models.BooleanField(default=False)),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="images",
                        to="products.product",
                    ),
                ),
            ],
            options={
                "verbose_name": "Product Image",
                "verbose_name_plural": "Product Images",
            },
        ),
        migrations.CreateModel(
            name="ProductVariant",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    django_extensions.db.fields.CreationDateTimeField(
                        auto_now_add=True, verbose_name="created"
                    ),
                ),
                (
                    "modified",
                    django_extensions.db.fields.ModificationDateTimeField(
                        auto_now=True, verbose_name="modified"
                    ),
                ),
                ("size", models.CharField(blank=True, max_length=50, null=True)),
                ("color", models.CharField(blank=True, max_length=50, null=True)),
                ("stock", models.IntegerField(help_text="Available quantity in stock")),
                (
                    "stock_unit",
                    models.IntegerField(
                        choices=[
                            (1, "kg"),
                            (2, "gm"),
                            (3, "ltr"),
                            (4, "ml"),
                            (5, "unit"),
                        ],
                        help_text="Unit of measurement for stock",
                    ),
                ),
                ("selling_price", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "sku",
                    models.CharField(
                        help_text="Stock Keeping Unit", max_length=50, unique=True
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="variants",
                        to="products.product",
                    ),
                ),
            ],
            options={
                "verbose_name": "Product Variant",
                "verbose_name_plural": "Product Variants",
            },
        ),
        migrations.AddIndex(
            model_name="product",
            index=models.Index(fields=["name"], name="products_pr_name_9ff0a3_idx"),
        ),
        migrations.AddIndex(
            model_name="product",
            index=models.Index(fields=["sku"], name="products_pr_sku_ca0cdc_idx"),
        ),
        migrations.AddIndex(
            model_name="product",
            index=models.Index(fields=["slug"], name="products_pr_slug_3edc0c_idx"),
        ),
    ]