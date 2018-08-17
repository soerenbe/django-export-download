# django-export-download

`django-export-download` allows you to use your ListView to download it in different file formats
like CSV or XLS by just adding the Mixin and add a new URL to your `urls.py`

It provides a MultipleObject/ListView Mixin for Django and add a classmethod `as_download()` method. 
You can use this view to download the object list in different file fomats like CSV, XLS and more. 
You just have to provide a `Resource` class from `django-import-export`.

I addition it work very good in you `django-tables2`/`django-filter` environment.

Finally the package ships with a templatetag to include some download buttons in your ListView template.


# Requirements
I tested the package with following versions, but it also should 
work with newer or older versions

* Django >= 1.11
* django-import-export >= 1.0.0
* Python >= 3.5

# Quickstart

```python
views.py:

from import_export import resources
from export_download.views import ExportDownloadView
from django.views.generic import ListView


class MovieBudgetResource(resources.ModelResource):
    class Meta:
        model = Movie
        fields = ['title', 'budget']


class MovieListView(ExportDownloadView, ListView):
    model = Movie
    resource_class = MovieBudget
    
urls.py:

urlpatterns = [
    path('movie/', MovieListView.as_view(), name='movie-list'),
    path('movie/export/', MovieListView.as_download(), name='movie-export'),
]
```

By visiting http://localhost:8000/movie/export you can download a CSV (which is the default) file with the movies 
and their budget.

http://localhost:8000/movie/export?resource_format=xls will download a Excel file.
# Dokumentation

## Class Options
Here is a more complex example that includes several `Resources` and different file formats.
It also is a example how to use `django-export-download` with `django-filter` and `django-tables2`.
```python

import django_tables2 as table
from import_export import resources
from export_download.views import ExportDownloadView
from django.views.generic import ListView
    

class MovieResource(resources.ModelResource):
    class Meta:
        model = Movie
        fields = ['title', 'budget', 'tatus', 'votes', 'release_date']
       
class OnlyMovieResource(resources.ModelResource):
    class Meta:
        model = Movie
        fields = ['title']

class MovieBudgetResource(resources.ModelResource):
    class Meta:
        model = Movie
        fields = ['title', 'budget']


class MovieListView(ExportDownloadView, ListView, table.SingleTableMixin):
    model = Movie
    table_class = MovieTable
    filter_class = MovieFilter

    resource_class = [
        MovieResource,
        OnlyMovieResource,
        MovieBudgetResource
    ]
    resource_formats = ['csv', 'tsv', 'xls']
```
This implementation support 3 download formats with 3 different `Resources`. Following URLs are giving 
you the files:

```
http://localhost:8000/movie/export/?resource_class=0&resource_format=xls
http://localhost:8000/movie/export/?resource_class=0&resource_format=csv
http://localhost:8000/movie/export/?resource_class=0&resource_format=tsv
http://localhost:8000/movie/export/?resource_class=1&resource_format=xls
http://localhost:8000/movie/export/?resource_class=1&resource_format=csv
http://localhost:8000/movie/export/?resource_class=1&resource_format=tsv
http://localhost:8000/movie/export/?resource_class=2&resource_format=xls
http://localhost:8000/movie/export/?resource_class=2&resource_format=csv
http://localhost:8000/movie/export/?resource_class=2&resource_format=tsv
```

Note that `resource_class` defines the position of the `Resource` implementation in the list of `resource_class`

In this example there also is a `filter_class`. `django-export-download` automatically applies the filter
to the queryset. It is not required, but works really well. Have a look at https://github.com/carltongibson/django-filter
for more information.

## Templatetags
`django-export-download` ships with a templatetag to render all links above. To use it your
download URL should point to the view name `<model_name>-export` or you have to overwrite the (simple) method
```python
def get_export_url(self, resource_class):
    return reverse('{}-export'.format(resource_class.Meta.model._meta.model_name))
```

You now can use the templatetag in you ListView
```html
{% load export_download %}

{% export_download_menu %}
```
# Contribute
Fork and send a PR