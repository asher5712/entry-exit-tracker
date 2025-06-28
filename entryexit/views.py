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
    ordering = '-timestamp'
    paginate_by = 100
    extra_context = {
        'edit_form': EntryExitRecordForm(),
        'form': EntryExitRecordForm(),
    }

    def get_queryset(self):
        queryset = super().get_queryset()
        if (
                self.request.user.is_superuser or
                self.request.user.is_staff
        ):
            return queryset
        return queryset.filter(user=self.request.user.pk)


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
