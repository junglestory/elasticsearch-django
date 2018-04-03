from django.shortcuts import render
from datetime import datetime, timedelta
import elasticsearch


def search(request):
    query = request.GET.get('query')
    sort = request.GET.get('sort')
    pageNum = request.GET.get('pageNum')
    fields = request.GET.get('fields')
    categorys = request.GET.get('categorys')
    startDate = request.GET.get('startDate')
    endDate = request.GET.get('endDate')

    index = "blogs"
    type = "blog"
    perPage = 10;
    from_ = (int(pageNum)-1) * int(perPage)
    searchFields = 'title,desc,author'
    searchFieldsName = ['Title', 'Desc', 'Author']

    if startDate == '' :
        startDate = (datetime.now() - timedelta(days=365)).strftime('%Y.%m.%d')

    if endDate == '' :
        endDate = datetime.today().strftime('%Y.%m.%d')

    if fields == '' :
        fields = searchFields

    form = {'query' : query, 'sort' : sort, 'pageNum' : pageNum, 'fields' : fields, 'categorys' : categorys, 'startDate' : startDate, 'endDate' : endDate, 'searchFields' : fields.split(',')}

    if query is not None:
        es_client = elasticsearch.Elasticsearch("localhost:9200")

        # Set sort query
        sortQuery = ''
        if sort == 'date' :
            sortQuery = {'date': 'desc'}
        else :
            sortQuery = {'_score': 'desc'}

        # Set date query
        dateQuery = ''
        if startDate != '' and endDate != '' :
            dateQuery = {'gte': startDate, 'lte': endDate}
        elif startDate != '' :
            dateQuery = {'gte': startDate}
        elif endDate != '' :
            dateQuery = {'lte': endDate}

        # Set range query
        rangeQuery = ''
        if dateQuery != '' :
            rangeQuery = {'date': dateQuery}

        # Set must query
        mustQuery = ''
        if rangeQuery != '' :
            mustQuery =[{'range': rangeQuery}, {'multi_match': {'query': query, 'fields': fields.split(',')}}]
        else :
            mustQuery = [{'multi_match': {'query': query, 'fields': fields.split(',')}}]

        # Set query
        searchQuery = ''
        if categorys != '' :
            searchQuery = {'must': mustQuery, 'filter': {'terms': {'category': categorys.split(',')}}}
        else :
            searchQuery = {'must': mustQuery}

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

        pageCount = ((docs['hits']['total'] - 1) / perPage) + 1
        pages = []

        if pageCount > 0 :
            for i in range(pageCount):
                pages.append(i+1)

        results = {'items' : items, 'totalCount' : docs['hits']['total'], 'pageCount' : pageCount, 'pages' : pages, 'buckets' : docs['aggregations']["group_by_category"]["buckets"]}
    return render(request, 'search.html' , {'form' : form, 'index' : index, 'searchFieldsName' : searchFieldsName, 'results' : results})