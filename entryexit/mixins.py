from datetime import datetime

from django.contrib.auth.mixins import UserPassesTestMixin


class OwnerUserMixin(UserPassesTestMixin):
    def test_func(self):
        record = self.get_object()
        return self.request.user == record.user


class RecordQuerysetMixin:
    """
    Encapsulates:
      - per-user filtering (superusers see all; others only their own)
      - optional timestamp range filtering via ?start_date=YYYY-MM-DD
        and/or ?end_date=YYYY-MM-DD
      - sorting via ?sort=...&direction=...
    """
    # same as your ListView
    allowed_sort_fields = {
        'timestamp': 'timestamp',
        'record_type': 'record_type',
        'user': 'user__username',
    }

    def filter_queryset(self, queryset):
        start_date = self.request.GET.get('start_date')
        end_date   = self.request.GET.get('end_date')
        if start_date:
            try:
                sd = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(timestamp__date__gte=sd)
            except ValueError:
                pass
        if end_date:
            try:
                ed = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(timestamp__date__lte=ed)
            except ValueError:
                pass

        # 2. sorting
        sort      = self.request.GET.get('sort')
        direction = self.request.GET.get('direction')
        if sort not in self.allowed_sort_fields:
            sort = 'timestamp'
        if direction not in ('asc', 'desc'):
            direction = 'desc'

        order_field = self.allowed_sort_fields[sort]
        if direction == 'desc':
            order_field = '-' + order_field

        return queryset.order_by(order_field)
