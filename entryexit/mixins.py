from django.contrib.auth.mixins import UserPassesTestMixin


class OwnerUserMixin(UserPassesTestMixin):
    def test_func(self):
        record = self.get_object()
        return self.request.user == record.user
