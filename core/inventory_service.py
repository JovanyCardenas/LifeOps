from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import InventoryChange, InventoryItem


ITEM_FIELDS = (
    "name", "location", "quantity", "reorder_threshold", "is_food",
    "unit", "printed_date", "opened_on", "cooked_on", "frozen_on",
    "archived",
)


def snapshot(item):
    data = {field: getattr(item, field) for field in ITEM_FIELDS}
    data["quantity"] = str(item.quantity)
    for field in ("printed_date", "opened_on", "cooked_on", "frozen_on"):
        value = data[field]
        data[field] = value.isoformat() if value else None
    return data


@transaction.atomic
def change_inventory(
    *,
    user,
    action,
    values,
    item_id=None,
    expected_revision=None,
    source="lifeops",
    undoes=None,
    request_id=None,
    request_fingerprint="",
):
    if set(values) - set(ITEM_FIELDS):
        raise ValidationError("The update contains an unsupported field.")

    if action == "add":
        item = InventoryItem(user=user)
        before = {}
    else:
        item = InventoryItem.objects.filter(user=user, pk=item_id).first()
        if item is None:
            raise ValidationError("This inventory item is unavailable.")
        if item.revision != expected_revision:
            raise ValidationError("This item changed. Reload it and try again.")
        if item.archived and action != "undo":
            raise ValidationError("This inventory item is archived.")
        before = snapshot(item)

    for field, value in values.items():
        setattr(item, field, value)
    item.full_clean()

    if action == "add":
        item.revision = 1
        item.save()
    else:
        next_revision = item.revision + 1
        updated = InventoryItem.objects.filter(
            user=user, pk=item.pk, revision=expected_revision
        ).update(
            **{field: getattr(item, field) for field in ITEM_FIELDS},
            revision=next_revision,
            updated_at=timezone.now(),
        )
        if updated != 1:
            raise ValidationError("This item changed. Reload it and try again.")
        item.revision = next_revision

    InventoryChange.objects.create(
        user=user,
        item=item,
        source=source,
        action=action,
        before=before,
        after=snapshot(item),
        item_revision=item.revision,
        undoes=undoes,
        request_id=request_id,
        request_fingerprint=request_fingerprint,
    )
    return item