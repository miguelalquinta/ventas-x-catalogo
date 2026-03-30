from django.contrib.admin import AdminSite


class VentasAdminSite(AdminSite):
    site_header = "Administración - VENTAS X CATALOGO"
    site_title = "VENTAS X CATALOGO"
    index_title = "Panel de Control"
    
    def index(self, request, extra_context=None):
        """Personaliza el índice del admin para incluir un link al dashboard"""
        extra_context = extra_context or {}
        extra_context['dashboard_url'] = '/dashboard/'
        return super().index(request, extra_context=extra_context)
