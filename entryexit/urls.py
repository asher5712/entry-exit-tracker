from django.urls import path
from django.urls import register_converter

from entryexit.helpers import DateConverter
from entryexit.views import AddRecordView
from entryexit.views import DailyRecordDetailView
from entryexit.views import ExportRecordCSVView
from entryexit.views import DeleteRecordView
from entryexit.views import EditRecordView
from entryexit.views import IndexView
from entryexit.views import RecordListView


register_converter(DateConverter, 'date')
urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('records/', RecordListView.as_view(), name='record_list'),
    path('records/by-date/<date:day>/', DailyRecordDetailView.as_view(), name='record_by_date'),
    path('records/add/', AddRecordView.as_view(), name='add_record'),
    path('records/export/', ExportRecordCSVView.as_view(), name='export_record_csv'),
    path('records/<int:pk>/edit/', EditRecordView.as_view(), name='edit_record'),
    path('records/<int:pk>/delete/', DeleteRecordView.as_view(), name='delete_record'),
]
