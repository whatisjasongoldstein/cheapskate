from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required


class StaffRequiredMixin(object):
    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super(StaffRequiredMixin, self).dispatch(*args, **kwargs)
