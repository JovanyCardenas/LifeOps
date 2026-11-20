from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.views.generic import FormView

from .forms import InventoryItemForm
from .inventory_service import change_inventory
from .models import InventoryChange, InventoryItem
from .views import OwnedQuerysetMixin


class InventoryEditor(OwnedQuerysetMixin, FormView):
    model = InventoryItem
    form_class = InventoryItemForm
    template_name = "core/item_form.html"

    def get_queryset(self):
        return super().get_queryset().filter(archived=False)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if "pk" in self.kwargs:
            kwargs["instance"] = get_object_or_404(
                self.get_queryset(), pk=self.kwargs["pk"]
            )
        return kwargs

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            module_title="Inventory",
            action="Edit" if "pk" in self.kwargs else "Add",
            **kwargs,
        )

    def form_valid(self, form):
        values = form.cleaned_data.copy()
        revision = values.pop("revision")
        item_id = self.kwargs.get("pk")
        try:
            change_inventory(
                user=self.request.user,
                action="edit" if item_id else "add",
                item_id=item_id,
                expected_revision=revision,
                values=values,
            )
        except ValidationError as error:
            # The existing form template displays errors attached to fields.
            form.add_error("quantity", error)
            return self.form_invalid(form)
        return HttpResponseRedirect(self.request.path) if False else redirect(
            "module_list", module="inventory"
        )


@login_required
def archive_item(request, pk):
    item = get_object_or_404(
        InventoryItem, pk=pk, user=request.user, archived=False
    )
    if request.method == "POST":
        try:
            revision = int(request.POST.get("revision", ""))
            change_inventory(
                user=request.user,
                action="archive",
                item_id=item.pk,
                expected_revision=revision,
                values={"archived": True},
            )
        except (ValueError, ValidationError):
            return HttpResponseBadRequest(
                "This item could not be archived. Open Inventory and try again."
            )
        return redirect("module_list", module="inventory")

    return render(request, "core/inventory_archive.html", {"item": item})


@login_required
def inventory_activity(request):
    changes = (
        InventoryChange.objects.filter(user=request.user)
        .select_related("item", "reversal")[:100]
    )
    return render(request, "core/inventory_activity.html", {"changes": changes})


@login_required
@require_POST
def undo_inventory_change(request, pk):
    change = get_object_or_404(
        InventoryChange.objects.select_related("item"),
        pk=pk,
        user=request.user,
        item__user=request.user,
    )
    if change.action == "undo" or hasattr(change, "reversal"):
        return HttpResponseBadRequest("This change cannot be undone again.")

    try:
        change_inventory(
            user=request.user,
            action="undo",
            item_id=change.item_id,
            expected_revision=change.item_revision,
            values=change.before or {"archived": True},
            undoes=change,
        )
    except ValidationError:
        return HttpResponseBadRequest(
            "This item changed after that edit. Review its current values in Inventory."
        )
    return redirect("inventory_activity")