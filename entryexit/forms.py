from django import forms
from entryexit.models import EntryExitRecord

class EntryExitRecordForm(forms.ModelForm):
    class Meta:
        model = EntryExitRecord
        fields = ['record_type']
