from django.shortcuts import render
from datetime import datetime, timedelta
import elasticsearch


def search(request):
    query = request.GET.get('query', '')
    sort = request.GET.get('sort', '_score')
    pageNum = request.GET.get('pageNum', 0)
    fields = request.GET.get('fields', '')
    categorys = request.GET.get('categorys', '')
    startDate = request.GET.get('startDate', '')
    endDate = request.GET.get('endDate', '')

    index = "blogs"
    type = "blog"
    perPage = 10;
    from_ = (int(pageNum)-1) * int(perPage)
    totalCount = 0;
    searchFields = 'title,desc,author'
    searchFieldsName = ['Title', 'Desc', 'Author']
    results = {}

    if endDate == '' :
        endDate = datetime.today().strftime('%Y.%m.%d')

    if startDate == '' :
        startDate = (datetime.combine(datetime.strptime(endDate, "%Y.%m.%d").date(), datetime.min.time()) - timedelta(days=365)).strftime('%Y.%m.%d')

    if fields == '' :
        fields = searchFields

    form = {'query' : query, 'sort' : sort, 'pageNum' : pageNum, 'fields' : fields, 'categorys' : categorys, 'startDate' : startDate, 'endDate' : endDate, 'searchFields' : searchFields.split(',')}

    if query != '':
        es_client = elasticsearch.Elasticsearch("localhost:9200")

        # Make sort query
        sortQuery = sort_query(sort)

        # Make date query
        dateQuery = date_query(startDate, endDate)

        # Make range query
        rangeQuery = range_query(dateQuery)

        # Make must query
        mustQuery = must_query(rangeQuery, fields, query)

        # Make search query
        searchQuery = search_query(categorys, mustQuery)

        print searchQuery
        docs = es_client.search(index=index,
                                doc_type=type,
                                from_=from_,
                                size=perPage,
                                body={
                                    'query': {
                                            'bool': searchQuery
                                        },
                                    'aggs': {
                                        'group_by_category': {
                                            'terms': {
                                                'field': 'category'
                                                }
                                            }
                                        },
                                    'sort': sortQuery,
                                    'highlight': {
                                            'pre_tags': ['<strong>'],
                                            'post_tags': ['</strong>'],
                                            'fields': {
                                                'title': {
                                                    'type': 'plain'
                                                },
                                                'desc': {
                                                    'type': 'plain'
                                                }
                                            }
                                        }
                                    }
                                )

        items = []
        for hits in docs['hits']['hits']:
            items.append(hits['_source'])

        totalCount = docs['hits']['total']

        pageCount = ((docs['hits']['total'] - 1) / perPage) + 1
        pages = []

        if pageCount > 0 :
            for i in range(pageCount):
                pages.append(i+1)

        results = {'items' : items, 'pageCount' : pageCount, 'pages' : pages, 'buckets' : docs['aggregations']["group_by_category"]["buckets"]}
    return render(request, 'search.html' , {'form' : form, 'index' : index, 'searchFieldsName' : searchFieldsName, 'totalCount' : totalCount, 'results' : results})

# Make sort query
def sort_query(sort) :
    value = '';

    if sort == 'date':
        value = {'date': 'desc'}
    else:
        value = {'_score': 'desc'}

    return value

# Make date query
def date_query(startDate, endDate):
    value = '';

    if startDate != '' and endDate != '':
        value = {'gte': startDate, 'lte': endDate}
    elif startDate != '':
        value = {'gte': startDate}
    elif endDate != '':
        value = {'lte': endDate}

    return value

# Make range query
def range_query(dateQuery):
    value = '';

    if dateQuery != '':
        value = {'date': dateQuery}

    return value

# Make must query
def must_query(rangeQuery, fields, query):
    value = '';

    if rangeQuery != '':
        value = [{'range': rangeQuery}, {'multi_match': {'query': query, 'fields': fields.split(',')}}]
    else:
        value = [{'multi_match': {'query': query, 'fields': fields.split(',')}}]

    return value

# Make search query
def search_query(categorys, mustQuery):
    value = '';

    if categorys != '':
        value = {'must': mustQuery, 'filter': {'terms': {'category': categorys.split(',')}}}
    else:
        value = {'must': mustQuery}

    return value