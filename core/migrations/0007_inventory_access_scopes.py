from django.db import migrations, models


def migrate_permissions(apps, schema_editor):
    Token = apps.get_model("core", "InventoryAccessToken")
    tokens = Token.objects.using(schema_editor.connection.alias)

    tokens.filter(can_write=False).update(scopes=["inventory:read"])
    tokens.filter(can_write=True).update(
        scopes=["inventory:read", "inventory:write"]
    )


def restore_permissions(apps, schema_editor):
    Token = apps.get_model("core", "InventoryAccessToken")
    tokens = Token.objects.using(schema_editor.connection.alias)

    for token in tokens.iterator():
        tokens.filter(pk=token.pk).update(
            can_write="inventory:write" in token.scopes
        )


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0006_inventoryaccesstoken"),
    ]

    operations = [
        migrations.AddField(
            model_name="inventoryaccesstoken",
            name="scopes",
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.RunPython(migrate_permissions, restore_permissions),
        migrations.RemoveField(
            model_name="inventoryaccesstoken",
            name="can_write",
        ),
    ]