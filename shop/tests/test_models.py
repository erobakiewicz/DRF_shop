import pytest
from django.core.exceptions import ValidationError

from utils.constants import ErrorMessages
from utils.exceptions import GlobalProductLimitObjectDoesNotExist
from shop.models import GlobalProductLimit
from utils.factories import RegionFactory


@pytest.mark.django_db
class GlobalProductLimitTestCase:

    def test_cannot_create_two_global_limits(self):
        GlobalProductLimit.objects.create(limit_size=5)
        GlobalProductLimit.objects.create(limit_size=5)
        assert GlobalProductLimit.objects.count() == 1

    def test_get_global_limit_does_not_exist(self):
        with pytest.raises(GlobalProductLimitObjectDoesNotExist) as exc:
            GlobalProductLimit.get_global_limit()
            assert exc.messsage == ErrorMessages.GLOBAL_LIMIT_NOT_SET


@pytest.mark.django_db
class RegionTestCase:

    def test_cannot_create_region_with_closed_and_unlimited_access(self):
        with pytest.raises(ValidationError) as exc:
            RegionFactory(closed_access=True, unlimited_access=True)
            assert exc.value == ErrorMessages.REGION_ACCESS_ERROR
