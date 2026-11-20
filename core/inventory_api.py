import hashlib
import hmac
import os

from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from .models import InventoryItem, InventoryChange, InventoryItem

import json
from decimal import Decimal, InvalidOperation
from uuid import UUID

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, OperationalError, transaction
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .inventory_service import change_inventory

def get_inventory_owner(request):
    configured_hash = os.environ.get("LIFEOPS_INVENTORY_TOKEN_SHA256", "")
    owner_id = os.environ.get("LIFEOPS_INVENTORY_USER_ID", "")
    scheme, _, token = request.headers.get("Authorization", "").partition(" ")

    if (
        scheme.lower() != "bearer"
        or not token
        or len(configured_hash) != 64
        or not owner_id.isascii()
        or not owner_id.isdecimal()
    ):
        return None

    supplied_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    if not hmac.compare_digest(supplied_hash, configured_hash):
        return None

    return int(owner_id)


@never_cache
@require_GET
def inventory_list(request):
    owner_id = get_inventory_owner(request)
    if owner_id is None:
        response = JsonResponse({"error": "Unauthorized"}, status=401)
        response["WWW-Authenticate"] = "Bearer"
        return response

    items = (
        InventoryItem.objects.filter(
            user_id=owner_id,
            is_food=True,
            archived=False,
            quantity__gt=0,
        )
        .order_by("name", "pk")
        .values(
            "id", "name", "quantity", "unit", "location", "printed_date",
            "opened_on", "cooked_on", "frozen_on", "revision",
        )
    )

    return JsonResponse({"items": list(items)})

def inventory_error(message, status):
    return JsonResponse({"error": message}, status=status)


def inventory_result(change, *, replayed):
    return JsonResponse({
        "request_id": str(change.request_id),
        "change_id": change.pk,
        "item_id": change.item_id,
        "revision": change.item_revision,
        "recorded_quantity": change.after["quantity"],
        "unit": change.after["unit"],
        "replayed": replayed,
    }, status=200 if replayed else 201)


def inventory_replay(owner_id, request_id, fingerprint):
    change = InventoryChange.objects.filter(
        user_id=owner_id, request_id=request_id
    ).first()
    if change is None:
        return None
    if change.request_fingerprint != fingerprint:
        return inventory_error("This request ID was used for a different edit.", 409)
    return inventory_result(change, replayed=True)


@csrf_exempt
@never_cache
@require_POST
def inventory_write(request):
    # This route authenticates only with the inventory bearer token.
    owner_id = get_inventory_owner(request)
    if owner_id is None:
        response = inventory_error("Unauthorized", 401)
        response["WWW-Authenticate"] = "Bearer"
        return response

    if request.content_type != "application/json":
        return inventory_error("Send an application/json request.", 415)
    if len(request.body) > 4096:
        return inventory_error("Request is too large.", 413)

    try:
        data = json.loads(request.body)
        if not isinstance(data, dict):
            raise ValueError
        request_id = UUID(data["request_id"])
        operation = data["operation"]
        if operation not in ("add", "use", "set"):
            raise ValueError
        quantity_text = data["quantity"]
        if not isinstance(quantity_text, str) or len(quantity_text) > 32:
            raise ValueError
        quantity = Decimal(quantity_text)
        if not quantity.is_finite() or quantity < 0:
            raise ValueError
        if operation in ("add", "use") and quantity == 0:
            raise ValueError
        InventoryItem._meta.get_field("quantity").run_validators(quantity)
    except (KeyError, TypeError, ValueError, InvalidOperation, ValidationError):
        return inventory_error("Invalid request ID, operation, or quantity.", 400)

    fingerprint = hashlib.sha256(
        json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()

    try:
        with transaction.atomic():
            owner = get_user_model().objects.filter(pk=owner_id, is_active=True).first()
            if owner is None:
                return inventory_error("Unauthorized", 401)

            previous = inventory_replay(owner_id, request_id, fingerprint)
            if previous is not None:
                return previous

            if operation == "add":
                name = data.get("name")
                unit = data.get("unit", "count")
                location = data.get("location", "")
                if (
                    not isinstance(name, str) or not name.strip()
                    or not isinstance(unit, str) or not unit.strip()
                    or not isinstance(location, str)
                ):
                    return inventory_error("Provide a name, unit, and valid location.", 400)
                item_id = None
                revision = None
                action = "add"
                values = {
                    "name": name.strip(),
                    "unit": unit.strip(),
                    "location": location.strip(),
                    "quantity": quantity,
                    "is_food": True,
                }
            else:
                item_id = data.get("item_id")
                revision = data.get("expected_revision")
                if (
                    type(item_id) is not int or not 0 < item_id <= 2**63 - 1
                    or type(revision) is not int or revision < 0
                ):
                    return inventory_error("Provide an item ID and expected revision.", 400)

                item = InventoryItem.objects.filter(
                    user_id=owner_id, pk=item_id, is_food=True, archived=False
                ).first()
                if item is None:
                    return inventory_error("Food batch not found.", 404)
                if item.revision != revision:
                    return inventory_error("Inventory changed. Read it again before editing.", 409)
                if data.get("unit") != item.unit:
                    return inventory_error(f"Send the quantity in {item.unit}.", 400)
                if operation == "use" and quantity > item.quantity:
                    return inventory_error("The amount used exceeds the stock on hand.", 400)

                action = "edit"
                values = {
                    "quantity": item.quantity - quantity if operation == "use" else quantity,
                }

            change_inventory(
                user=owner,
                action=action,
                values=values,
                item_id=item_id,
                expected_revision=revision,
                source="ChatGPT via Desktop Commander",
                request_id=request_id,
                request_fingerprint=fingerprint,
            )
            change = InventoryChange.objects.get(user_id=owner_id, request_id=request_id)

        return inventory_result(change, replayed=False)

    except ValidationError as error:
        previous = inventory_replay(owner_id, request_id, fingerprint)
        if previous is not None:
            return previous
        current = InventoryItem.objects.filter(
            user_id=owner_id, pk=item_id, is_food=True, archived=False
        ).first()
        if item_id is not None and (current is None or current.revision != revision):
            return inventory_error("Inventory changed. Read it again before editing.", 409)
        return inventory_error(" ".join(error.messages), 400)
    except IntegrityError:
        previous = inventory_replay(owner_id, request_id, fingerprint)
        if previous is not None:
            return previous
        if InventoryChange.objects.filter(request_id=request_id).exists():
            return inventory_error("Request ID is already in use.", 409)
        raise
    except OperationalError as error:
        if "locked" in str(error).lower():
            return inventory_error("Database is busy. Retry with the same request ID.", 503)
        raise