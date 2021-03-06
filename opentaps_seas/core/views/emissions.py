# This file is part of opentaps Smart Energy Applications Suite (SEAS).

# opentaps Smart Energy Applications Suite (SEAS) is free software:
# you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# opentaps Smart Energy Applications Suite (SEAS) is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with opentaps Smart Energy Applications Suite (SEAS).
# If not, see <https://www.gnu.org/licenses/>.

import logging

from .common import WithBreadcrumbsMixin
from .. import emissions_utils
from ..models import Meter

from ..models import SiteView

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse
from django.views.generic import DetailView
from rest_framework.decorators import api_view


logger = logging.getLogger(__name__)


class CreateEmissions(LoginRequiredMixin, WithBreadcrumbsMixin, DetailView):
    model = Meter
    slug_field = "meter_id"
    slug_url_kwarg = "meter_id"
    template_name = "core/emissions_create_emissions.html"

    def get_context_data(self, **kwargs):
        context = super(CreateEmissions, self).get_context_data(**kwargs)
        context["meter_id"] = self.kwargs["meter_id"]

        try:
            meter = Meter.objects.get(meter_id=self.kwargs["meter_id"])
        except Meter.DoesNotExist:
            pass
        else:
            if meter.utility_id:
                context["utility_id"] = meter.utility_id
            if meter.account_number:
                context["account_number"] = meter.account_number

        return context

    def get_breadcrumbs(self, context):
        b = []
        b.append({"url": reverse("core:site_list"), "label": "Sites"})
        meter = None
        if self.kwargs["meter_id"]:
            try:
                meter = Meter.objects.get(meter_id=self.kwargs["meter_id"])
            except Meter.DoesNotExist:
                pass
            else:
                try:
                    site = SiteView.objects.get(entity_id=meter.site_id)
                except SiteView.DoesNotExist:
                    pass
                else:
                    label = "Site"
                    if site.description:
                        label = site.description
                    url = reverse("core:site_detail", kwargs={"site": meter.site_id})
                    b.append({"url": url, "label": label})

        if meter:
            url = reverse("core:meter_detail", kwargs={"meter_id": meter.meter_id})
            label = "Meter " + meter.meter_id
            if meter.description:
                label = "Meter " + meter.description
            b.append({"url": url, "label": label})

        b.append({"label": "Create Emissions"})
        return b


create_emissions = CreateEmissions.as_view()


@login_required()
@api_view(["POST"])
def record_emissions(request):
    if request.method == "POST":
        data = request.data
        user_id = data.get("user_id")
        org_name = data.get("org_name")
        utility_id = data.get("utility_id")
        account_number = data.get("account_number")
        from_date = data.get("from_date")
        thru_date = data.get("thru_date")
        amount = data.get("amount")
        uom = data.get("uom")

        emissions_data = emissions_utils.record_emissions(
            user_id,
            org_name,
            utility_id,
            account_number,
            from_date,
            thru_date,
            amount,
            uom,
        )

        if emissions_data:
            return JsonResponse({"success": 1, "emissions_data": emissions_data})
        else:
            return JsonResponse({"error": "Cannot record emissions"})
