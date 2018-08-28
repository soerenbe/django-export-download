from django.http import HttpResponseNotAllowed, Http404, HttpResponse
from django.views.generic.list import ListView

from import_export.formats import base_formats
from import_export.resources import Resource


class ResourceDownloadMixin:
    resource_class = None

    resource_formats = ['csv', 'xls']

    resource_class_parameter = 'resource_class'
    resource_format_parameter = 'resource_format'

    _resource_format_map = {
        'csv': base_formats.CSV,
        'xls': base_formats.XLS,
        'json': base_formats.JSON,
        'yaml': base_formats.YAML,
        'tsv': base_formats.TSV,
    }

    _download_parameter = 'download'

    def _sanity_check(self):
        cn = self.__class__.__name__
        assert issubclass(self.__class__, ListView), \
            'You can use the ExportDownloadMixin only in a ListView'
        assert self._get_ressource_classes(), \
            'Object {}.resource_class must be defined.'.format(cn)
        for k in self._get_ressource_classes():
            assert issubclass(k, Resource), \
                'Object {} in {}.resource_class is not a instance of import_export.resources.Resource'.format(k, cn)

        assert type(self.resource_formats) is list, \
            'Format {} in {}.resource_formats is not a valid resource_format'.format(self.resource_formats, cn)
        assert len(self.resource_formats) > 0, \
            'Format {} in {}.resource_formats must not be empty'.format(self.resource_formats, cn)
        for f in self.resource_formats:
            assert f in self._resource_format_map, \
                'Format {} in {}.resource_class is not a valid resource_formats'.format(f, cn)

    def _get_ressource_classes(self):
        """
        Format the resource classes
        """
        if self.resource_class is None:
            return []
        elif isinstance(self.resource_class, list):
            return self.resource_class
        else:
            return [self.resource_class]

    def get_resource_links(self, request):
        """
        This method return a dict in the form:
        {
            '<resource_format>': ['<download_link>', '<description>'],
            ...
        }

        It is only used when using the export_download_menu templatetag
        """
        resource_links = {}

        for f in self.resource_formats:
            resource_links[f.lower()] = []
            for counter, resource_class in enumerate(self._get_ressource_classes()):
                params = request.GET.copy()
                params_class = {
                    self.resource_class_parameter: counter,
                    self.resource_format_parameter: f,
                }
                params.update(params_class)
                link = "?" + self._to_url_params(params)
                # if there is a description field in the resource class
                # we use it to display it as a description
                description = getattr(resource_class, 'description', resource_class.__name__)
                resource_links[f.lower()].append([link, description])
        return resource_links

    def _to_url_params(self, d):
        """
        return a kwarg in GET parameter format
        """
        return self._download_parameter + "&" + "&".join('{}={}'.format(k, v) for k, v in d.items())

    def render_to_response(self, *args, **kwargs):
        if self._download_parameter in self.request.GET:
            return self.render_to_download_response(*args, **kwargs)
        return super().render_to_response(*args, **kwargs)

    def render_to_download_response(self, *args, **kwargs):
        self._sanity_check()
        if self.request.method != 'GET':
            return HttpResponseNotAllowed(['GET'])
        # We use the first resource class and first resource format
        # as a default, when there are no parameters
        resource_class = self.request.GET.get(self.resource_class_parameter, 0)
        resource_format = self.request.GET.get(self.resource_format_parameter, self.resource_formats[0])
        if not resource_format:
            raise Http404('You have to pass {} as GET parameter'.format(self.resource_format_parameter))

        selected_format = self._resource_format_map.get(resource_format, None)
        if not selected_format:
            raise Http404('Export format {} not found'.format(resource_format))

        try:
            resource_class_number = int(resource_class)
        except:
            raise Http404('Parameter {} must be an integer'.format(self.resource_class_parameter))
        if resource_class_number >= len(self._get_ressource_classes()):
            raise Http404('Parameter {}.{} does not exist'.format(self.__class__.__name__, self.resource_class_parameter))

        qs = self.model.objects.all()
        # If filer_class is defined try to filter against it.
        # You need django-filter to use this feature.
        if hasattr(self, 'filter_class'):
            if self.filter_class:
                qs = self.filter_class(self.request.GET, queryset=qs).qs
        resource_class = self._get_ressource_classes()[resource_class_number]
        export = resource_class().export(qs)
        r = getattr(export, selected_format.__name__.lower())
        return HttpResponse(r, content_type=selected_format.CONTENT_TYPE)
