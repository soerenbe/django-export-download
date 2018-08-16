from django.http import HttpResponseNotAllowed, Http404, HttpResponse
from django.urls import reverse
from django.views.generic.list import MultipleObjectMixin

from import_export.formats import base_formats
from import_export.resources import Resource


class ExportDownloadView(MultipleObjectMixin):
    resource_class = None

    _resource_format_map = {
        'csv': base_formats.CSV,
        'xls': base_formats.XLS,
        'json': base_formats.JSON,
        'yaml': base_formats.YAML,
        'tsv': base_formats.TSV,
    }

    resource_class_parameter = 'resource_class'
    resource_format_parameter = 'resource_format'

    resource_formats = ['csv', 'xls']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self._get_ressource_classes():
            raise NotImplementedError('Object {}.resource_class must be defined.'.format(self.__class__.__name__))
        for k in self._get_ressource_classes():
            if not issubclass(k, Resource):
                raise NotImplementedError('Object {} in {}.resource_class is not a instance of '
                                          'import_export.resources.Resource'.format(k, self.__class__.__name__))

        if not self.resource_formats or len(self.resource_formats) == 0:
            raise NotImplementedError('Format {} in {}.resource_formats is not a valid '
                                      'resource_format'.format(self.resource_formats, self.__name__))
        for f in self.resource_formats:
            if f not in self._resource_format_map:
                raise NotImplementedError('Format {} in {}.resource_class is not a valid '
                                          'resource_formats'.format(f, self.__name__))

    def get_export_url(self, resource_class):
        return reverse('{}-export'.format(resource_class.Meta.model._meta.model_name))

    @classmethod
    def _get_ressource_classes(cls):
        if cls.resource_class is None:
            return []
        elif isinstance(cls.resource_class, list):
            return cls.resource_class
        else:
            return [cls.resource_class]

    def _get_resource_links(self, request):
        resource_links = {}

        for f in self.resource_formats:
            resource_links[f.lower()] = []
            for counter, resource_class in enumerate(self._get_ressource_classes()):
                export_url = self.get_export_url(resource_class)
                params = request.GET.copy()
                params_class = {
                    self.resource_class_parameter: counter,
                    self.resource_format_parameter: f,
                }
                params.update(params_class)
                link = export_url + "?" + self._to_url_params(params)
                description = getattr(resource_class, 'description', resource_class.__name__)
                resource_links[f.lower()].append([link, description])
        return resource_links

    @staticmethod
    def _to_url_params(d):
        return "&".join('{}={}'.format(k, v) for k, v in d.items())

    @classmethod
    def as_download(cls, *args, **kwargs):

        def view(request, *args, **kwargs):
            if request.method != 'GET':
                return HttpResponseNotAllowed(['GET'])
            resource_class = request.GET.get(cls.resource_class_parameter, cls.resource_formats[0])
            resource_format = request.GET.get(cls.resource_format_parameter, cls._get_ressource_classes()[0])

            if not resource_class:
                raise Http404('You have to pass {} as GET parameter'.format(cls.resource_class_parameter))
            if not resource_format:
                raise Http404('You have to pass {} as GET parameter'.format(cls.resource_format_parameter))

            selected_format = cls._resource_format_map.get(resource_format, None)
            if not selected_format:
                raise Http404('Export format {} not found'.format(resource_format))

            try:
                resource_class_number = int(resource_class)
            except:
                raise Http404('Parameter {} must be an integer'.format(cls.resource_class_parameter))

            qs = cls.model.objects.all()
            # If filer_class is defined try to filter against it.
            # You need django-filter to use this feature.
            if hasattr(cls, 'filter_class'):
                if cls.filter_class:
                    qs = cls.filter_class(request.GET, queryset=qs).qs
            resource_class = cls._get_ressource_classes()[resource_class_number]
            export = resource_class().export(qs)
            r = getattr(export, selected_format.__name__.lower())
            return HttpResponse(r, content_type=selected_format.CONTENT_TYPE)

        return view
