# elasticsearch-django
This application is a sample for Elasticsearch client with Django and Bootstrap.

## Features
* MultiMatchQuery
* Hightlight
* Date Range
* Filter
* Sort
* Aggregation
* Paginated

## Requirements
* [Python](https://www.python.org/downloads/) requires 2.7 or higher
* [pip](https://pip.pypa.io/en/stable/installing/) requires 1.5 or higher
* [Django](https://docs.djangoproject.com/ko/2.0/topics/install/#installing-official-release) requires 1.8 or higher
* Elasticsearch requires 6.2 or higher

## Soruce code clone
```shell
$ git clone https://github.com/junglestory/elasticsearch-django.git
$ cd elasticsearch-django
$ python manage.py migrate
```

## Installation
* [Download](https://www.elastic.co/downloads/elasticsearch) and unzip the Elasticsearch official distribution.
* Run bin\elasticsearch
* Run curl -X GET http://localhost:9200/
* [Sampe data](https://github.com/junglestory/scrape_blog_crawler)


## Develoment Server
Run `python manage.py runserver` for a dev server. Navigate to `http://localhost:8000/search`.
