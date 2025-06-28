from django.urls import path

from entryexit.views import AddRecordView, RecordListView, IndexView, EditRecordView, DeleteRecordView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('records/', RecordListView.as_view(), name='record_list'),
    path('records/add/', AddRecordView.as_view(), name='add_record'),
    path('records/<int:pk>/edit/', EditRecordView.as_view(), name='edit_record'),
    path('records/<int:pk>/delete/', DeleteRecordView.as_view(), name='delete_record'),
]
