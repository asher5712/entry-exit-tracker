from django.contrib.auth.mixins import LoginRequiredMixin
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


class RecordListView(LoginRequiredMixin, ListView):
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
        if self.request.user.is_superuser:
            return EntryExitRecord.objects.all()
        return EntryExitRecord.objects.filter(user=self.request.user.pk)


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
