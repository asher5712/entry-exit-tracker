from django.urls import path

from entryexit.views import AddRecordView
from entryexit.views import ExportRecordCSVView
from entryexit.views import DeleteRecordView
from entryexit.views import EditRecordView
from entryexit.views import IndexView
from entryexit.views import RecordListView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('records/', RecordListView.as_view(), name='record_list'),
    path('records/add/', AddRecordView.as_view(), name='add_record'),
    path('records/export/', ExportRecordCSVView.as_view(), name='export_record_csv'),
    path('records/<int:pk>/edit/', EditRecordView.as_view(), name='edit_record'),
    path('records/<int:pk>/delete/', DeleteRecordView.as_view(), name='delete_record'),
]
