from products.models import Category
from core.models import SiteSettings


def common_data(request):
    return {"categories": Category.objects.all()[:5], "settings": SiteSettings.load()}
