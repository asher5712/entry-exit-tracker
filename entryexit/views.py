from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import ListView
from django.views.generic import UpdateView

from entryexit.forms import EntryExitRecordForm
from entryexit.mixins import OwnerUserMixin
from entryexit.models import EntryExitRecord


# Create your views here.
class IndexView(View):
    @staticmethod
    def get(request, *args, **kwargs):
        return HttpResponseRedirect(reverse_lazy('record_list'))


class RecordListView(PermissionRequiredMixin, ListView):
    permission_required = 'entryexit.view_entryexitrecord'
    permission_denied_message = "Permission Denied"
    template_name = 'entryexit/record_list.html'
    context_object_name = 'records'
    model = EntryExitRecord
    paginate_by = 8

    # keep your forms around for the modals
    extra_context = {
        'edit_form': EntryExitRecordForm(),
        'form': EntryExitRecordForm(),
    }

    # define which query‐params map to real model fields
    allowed_sort_fields = {
        'timestamp': 'timestamp',
        'record_type': 'record_type',
        'user': 'user__username',
    }

    def get_queryset(self):
        qs = super().get_queryset()

        # non‐superusers only see their own
        if not (self.request.user.is_superuser or self.request.user.is_staff):
            qs = qs.filter(user=self.request.user)

        # grab & validate sort params
        sort = self.request.GET.get('sort')
        direction = self.request.GET.get('direction')
        if sort not in self.allowed_sort_fields:
            sort = 'timestamp'
        if direction not in ('asc', 'desc'):
            direction = 'desc'

        order_field = self.allowed_sort_fields[sort]
        if direction == 'desc':
            order_field = '-' + order_field

        return qs.order_by(order_field)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # echo back to the template so headers can highlight/toggle
        ctx['current_sort'] = self.request.GET.get('sort', 'timestamp')
        ctx['current_direction'] = self.request.GET.get('direction', 'desc')
        return ctx


class AddRecordView(PermissionRequiredMixin, CreateView):
    permission_required = 'entryexit.add_entryexitrecord'
    permission_denied_message = "Permission Denied"
    success_url = reverse_lazy('record_list')
    form_class = EntryExitRecordForm
    model = EntryExitRecord

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class EditRecordView(PermissionRequiredMixin, OwnerUserMixin, UpdateView):
    permission_required = 'entryexit.change_entryexitrecord'
    permission_denied_message = "Permission Denied"
    success_url = reverse_lazy('record_list')
    template_name = 'entryexit/edit_record.html'
    form_class = EntryExitRecordForm
    model = EntryExitRecord


class DeleteRecordView(PermissionRequiredMixin, OwnerUserMixin, DeleteView):
    permission_required = 'entryexit.delete_entryexitrecord'
    permission_denied_message = "Permission Denied"
    template_name = 'entryexit/delete_record.html'
    success_url = reverse_lazy('record_list')
    model = EntryExitRecord
