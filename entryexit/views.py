from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

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
    raise_exception = True
    paginate_by = 100
    extra_context = {
        'edit_form': EntryExitRecordForm(),
        'form': EntryExitRecordForm(),
    }


class AddRecordView(LoginRequiredMixin, CreateView):
    success_url = reverse_lazy('record_list')
    form_class = EntryExitRecordForm
    model = EntryExitRecord

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class EditRecordView(LoginRequiredMixin, OwnerUserMixin, UpdateView):
    success_url = reverse_lazy('record_list')
    template_name = 'entryexit/edit_record.html'
    form_class = EntryExitRecordForm
    model = EntryExitRecord


class DeleteRecordView(LoginRequiredMixin, OwnerUserMixin, DeleteView):
    template_name = 'entryexit/delete_record.html'
    success_url = reverse_lazy('record_list')
    model = EntryExitRecord
