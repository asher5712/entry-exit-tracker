import csv
from datetime import timedelta
from zoneinfo import ZoneInfo

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import F
from django.db.models import Q
from django.db.models.aggregates import Max
from django.db.models.aggregates import Min
from django.db.models.functions import TruncDate
from django.http import HttpResponseRedirect
from django.http import StreamingHttpResponse
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.timezone import localdate
from django.views import View
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import ListView
from django.views.generic import UpdateView

from entryexit.filters import EntryExitRecordFilter
from entryexit.forms import EntryExitRecordForm
from entryexit.helpers import Echo
from entryexit.mixins import OwnerUserMixin
from entryexit.models import EntryExitRecord


# Create your views here.
class IndexView(View):
    @staticmethod
    def get(request, *args, **kwargs):
        return HttpResponseRedirect(reverse_lazy('record_list'))


class RecordListView(PermissionRequiredMixin, ListView):
    """
    One-row-per-date overview, with first-IN / last-OUT side by side,
    django-filters for date-range, sortable by date/user, paginated.
    """

    permission_required = 'entryexit.view_entryexitrecord'
    template_name = 'entryexit/record_list.html'
    filterset_class = EntryExitRecordFilter
    context_object_name = 'daily_records'
    model = EntryExitRecord
    paginate_by = 8

    # keep your forms around for the modals
    extra_context = {
        'form': EntryExitRecordForm(),
    }

    def get_queryset(self):
        qs = super().get_queryset()

        # non‐superusers only see their own
        if not (self.request.user.is_superuser or self.request.user.is_staff):
            qs = qs.filter(user=self.request.user)

        # 2) Apply django-filter date-range
        qs = self.filterset_class(self.request.GET, queryset=qs).qs

        # 3) Annotate calendar date
        qs = qs.annotate(date=TruncDate('timestamp'))

        # 4) Determine ordering from GET?sort & ?direction
        sort = self.request.GET.get('sort', 'date')
        direction = self.request.GET.get('direction', 'desc')
        allowed = ['date'] + (['user'] if self.request.user.is_superuser else [])
        if sort not in allowed:
            sort = 'date'
        if direction not in ('asc', 'desc'):
            direction = 'desc'

        if sort == 'user':
            order_field = 'user__username'
        else:
            order_field = 'date'
        if direction == 'desc':
            order_field = '-' + order_field

        # 5) Group & pick first-IN / last-OUT
        group_fields = ['date']
        if self.request.user.is_superuser:
            group_fields.insert(0, 'user__username')

        daily = (
            qs
            .values(*group_fields)
            .annotate(
                first_in = Min('timestamp', filter=Q(record_type=EntryExitRecord.ENTRY)),
                last_out = Max('timestamp', filter=Q(record_type=EntryExitRecord.EXIT))
            )
            .order_by(order_field)
        )

        return daily

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # echo back for header links & export URL
        ctx['current_sort'] = self.request.GET.get('sort', 'date')
        ctx['current_direction'] = self.request.GET.get('direction', 'desc')
        ctx['current_start'] = self.request.GET.get('start_date', '')
        ctx['current_end'] = self.request.GET.get('end_date', '')
        return ctx

class DailyRecordDetailView(PermissionRequiredMixin, ListView):
    """
    Shows the actual EntryExitRecord objects for one date so you can edit/delete.
    """

    permission_required = 'entryexit.view_entryexitrecord'
    template_name = 'entryexit/daily_detail.html'
    context_object_name = 'records'

    extra_context = {
        'edit_form': EntryExitRecordForm(),
        'form': EntryExitRecordForm(),
    }

    def get_queryset(self):
        # reuse django-filter & per-user if you like, or just per-user + date
        qs = EntryExitRecord.objects.all()
        if not (self.request.user.is_superuser or self.request.user.is_staff):
            qs = qs.filter(user=self.request.user)
        # filter by the chosen day
        return qs.filter(timestamp__date=self.kwargs['day']).order_by('timestamp')


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


class ExportRecordCSVView(PermissionRequiredMixin, View):
    """
    Streams the current user's (and date-filtered) EntryExitRecord queryset as CSV.
    """

    permission_required = 'entryexit.export_entryexitrecord'
    permission_denied_message = "Permission Denied"
    filterset_class = EntryExitRecordFilter

    def get_queryset(self):
        queryset = EntryExitRecord.objects.all()

        if not (self.request.user.is_superuser or self.request.user.is_staff):
            queryset = queryset.filter(user=self.request.user)

        # apply the same date-range filter
        queryset = self.filterset_class(self.request.GET, queryset=queryset).qs
        return queryset

    def format_duration(self, delta: timedelta) -> str:
        total_seconds = int(delta.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def get(self, request, *args, **kwargs):
        pseudo_buffer = Echo()
        writer = csv.writer(pseudo_buffer)

        # Build filename:
        user_label = request.user.get_short_name() or request.user.username
        start = request.GET.get('start_date')
        end = request.GET.get('end_date')
        if start and end:
            fn_date = f"F{start.replace('-', '')}T{end.replace('-', '')}"
        else:
            fn_date = f"ALL{localdate().strftime('%Y%m%d')}"
        filename = f"{user_label.upper()}_ENTRY_EXIT_RECORDS_{fn_date}.csv"

        # 1) Base & filtered queryset
        qs = self.get_queryset()

        # 2) Annotate each record with its user’s timezone for later
        qs = qs.annotate(
            user_tz=F('user__profile__timezone'),
            date=TruncDate('timestamp')
        )

        # 3) Group by user + date, pick earliest IN / latest OUT
        daily = (
            qs
            .values('user__username', 'user__first_name', 'user__last_name', 'user_tz', 'date')
            .annotate(
                entry=Min('timestamp', filter=Q(record_type=EntryExitRecord.ENTRY)),
                exit =Max('timestamp', filter=Q(record_type=EntryExitRecord.EXIT)),
            )
            .order_by('user__username', 'date')
        )

        def row_generator():
            # BOM for Excel + header row
            yield '\ufeff'
            yield writer.writerow(['User', 'Date', 'Entry', 'Exit', 'Duration'])

            total_duration = timedelta()

            for row in daily:
                # build full_name or username
                first = row.get('user__first_name') or ''
                last = row.get('user__last_name') or ''
                full_name = f"{first} {last}".strip()
                user_cell = full_name if full_name else row['user__username']

                tz_name  = row['user_tz']
                entry_dt = row['entry']
                exit_dt  = row['exit']
                date_str = row['date'].strftime('%Y-%m-%d')

                # Helper to localize & format a timestamp
                def fmt(dt):
                    if not dt:
                        return '----'
                    try:
                        if tz_name:
                            user_zone = ZoneInfo(tz_name)
                            dt = dt.astimezone(user_zone)
                        else:
                            dt = timezone.localtime(dt)
                    except Exception:
                        dt = timezone.localtime(dt)
                    return dt.strftime('%H:%M%Z')

                entry_str = fmt(entry_dt)
                exit_str  = fmt(exit_dt)

                # Compute duration if both sides exist
                if entry_dt and exit_dt:
                    delta = exit_dt - entry_dt
                    total_duration += delta
                    duration_str = self.format_duration(delta)
                else:
                    duration_str = '----'

                yield writer.writerow([
                    user_cell,
                    date_str,
                    entry_str,
                    exit_str,
                    duration_str,
                ])

            # Final “Total” row
            total_str = self.format_duration(total_duration)
            yield writer.writerow([
                'Total', '', '', '', total_str
            ])

        # 4) Stream the response
        response = StreamingHttpResponse(
            row_generator(),
            content_type='text/csv; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
