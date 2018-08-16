from django import template

register = template.Library()


@register.inclusion_tag('export_download_menu.html', takes_context=True)
def export_download_menu(context, button_class='btn-default'):
    return {
        'resources': context['view']._get_resource_links(context['request']),
        'button_class': button_class,
    }
