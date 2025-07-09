from django_filters import DateFilter
from django_filters import FilterSet

from entryexit.models import EntryExitRecord


class EntryExitRecordFilter(FilterSet):
    start_date = DateFilter(
        field_name='timestamp',
        lookup_expr='date__gte',
        label='Start date'
    )
    end_date   = DateFilter(
        field_name='timestamp',
        lookup_expr='date__lte',
        label='End date'
    )

    class Meta:
        model = EntryExitRecord
        fields = ['start_date', 'end_date']
