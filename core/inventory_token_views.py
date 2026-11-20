import hashlib
import secrets

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods, require_POST

from .models import InventoryAccessToken


def check_token_settings_access(user):
    if user.get_username() == "demo" and not settings.LIFEOPS_ENABLE_DEMO:
        raise Http404


@never_cache
@login_required
@require_http_methods(["GET", "POST"])
def inventory_tokens(request):
    check_token_settings_access(request.user)
    raw_token = None
    error = None

    if request.method == "POST":
        label = request.POST.get("label", "").strip()
        mode = request.POST.get("mode")
        if not 1 <= len(label) <= 60 or mode not in {"read", "write"}:
            error = "Enter a name up to 60 characters and select a permission."
        else:
            raw_token = secrets.token_urlsafe(32)
            InventoryAccessToken.objects.create(
                user=request.user,
                label=label,
                token_hash=hashlib.sha256(raw_token.encode("ascii")).hexdigest(),
                can_write=(mode == "write"),
            )

    return render(request, "core/inventory_tokens.html", {
        "tokens": InventoryAccessToken.objects.filter(user=request.user),
        "raw_token": raw_token,
        "error": error,
        "api_url": request.build_absolute_uri(reverse("inventory_api_list")),
    }, status=400 if error else 200)


@login_required
@require_POST
def revoke_inventory_token(request, pk):
    check_token_settings_access(request.user)
    updated = InventoryAccessToken.objects.filter(
        user=request.user,
        pk=pk,
        revoked_at__isnull=True,
    ).update(revoked_at=timezone.now())
    if not updated:
        raise Http404
    return redirect("inventory_tokens")