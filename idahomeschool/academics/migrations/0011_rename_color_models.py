# Generated manually

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("academics", "0010_add_color_palette_groups"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Rename ColorPalette to Color
        migrations.RenameModel(
            old_name="ColorPalette",
            new_name="Color",
        ),
        # Rename ColorPaletteGroup to ColorPalette
        migrations.RenameModel(
            old_name="ColorPaletteGroup",
            new_name="ColorPalette",
        ),
        # Rename the M2M field from "groups" to "palettes"
        migrations.RenameField(
            model_name="color",
            old_name="groups",
            new_name="palettes",
        ),
        # Update the related_name on the user foreign key for Color
        migrations.AlterField(
            model_name="color",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="colors",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        # Update the related_name on the user foreign key for ColorPalette
        migrations.AlterField(
            model_name="colorpalette",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="color_palettes",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
