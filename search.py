from google.cloud import bigquery
import uuid
import datetime as dt

def n_days_whence(n):
    td = dt.datetime.now() # current precision does not necessitate specification of time zone
    seven_days = dt.timedelta(n)
    whence = td - seven_days
    formatted = '%04d-%02d-%02d' % (whence.year,whence.month,whence.day)

    return formatted

class Query():

    def __init__(self,log):
        self.client = bigquery.Client.from_service_account_json('service_account.json')
        self.log = log

        # previously determined; included for reference
        self.header = ['scene_id','product_id','spacecraft_id','sensor_id','date_acquired',
            'sensing_time','collection_number','collection_category','data_type','wrs_path',
            'wrs_row','cloud_cover','north_lat','south_lat','west_lon','east_lon','total_size',
            'base_url']

    def get_header(self):
        # https://google-cloud-python.readthedocs.io/en/latest/bigquery/usage.html#table-operations
        dataset_ref = self.client.dataset('cloud_storage_geo_index', project='bigquery-public-data')
        table_ref = dataset_ref.table('landsat_index')
        table = self.client.get_table(table_ref)  # API call

        # Load the first 10 rows
        rows = self.client.list_rows(table, max_results=10)

        # Specify selected fields to limit the results to certain columns
        fields = table.schema[:2]  # first two columns
        rows = self.client.list_rows(table, selected_fields=fields, max_results=10)

        # Use the start index to load an arbitrary portion of the table
        rows = self.client.list_rows(table, start_index=10, max_results=10)

        # Print row data in tabular format
        format_string = '{!s:<16} ' * len(rows.schema)
        field_names = [field.name for field in rows.schema]
        self.header = format_string.format(*field_names)

        # prints row data
        #for row in rows:
        #    print(format_string.format(*row))      

    def find_n_days_old(self,n,coordinates):
        '''
            Queries Google BigQuery to get urls from TIFFS uploaded within the last week.
            Returns URLS
        '''
        C = ''

        if coordinates != None:
            latitude, longitude = coordinates

            # points will match multiple slices even with half-open intervals, so
            # just use closed intervals to avoid accidental exclusion
            C = 'AND south_lat <= %s AND %s <= north_lat ' % (latitude, latitude)
            C = C + 'AND west_lon <= %s AND %s <= east_lon' % (longitude,longitude)

        query = ('''
            SELECT * FROM `bigquery-public-data.cloud_storage_geo_index.landsat_index`
            WHERE date_acquired >= \'%s\' %s ''' % (n_days_whence(n),C))

            # alternatively, use a variation of this:
            #'WHERE TIMESTAMP(date(a.date_acquired)) > DATE_ADD(USEC_TO_TIMESTAMP(NOW()), -1, \'WEEK\')'
            #'LIMIT 10' 

        job_config = bigquery.QueryJobConfig()

        query_job = self.client.query(query,location='US',job_config=job_config)

        self.log.info('Starting query, which is: \n %s' % query)

        count = 0
        url_list = {}
        for row in query_job:
        
            # brutish, but it gets what we need. row[17] corresponds to the URL column of a given
            # row returned by this SQL request
            url = row[17]

            url_list[url] = {'scene_id':row[0],'product_id':row[1],'spacecraft_id':row[2],
                'sensor_id':row[3],'date_acquired':row[4],'sensing_time':row[5],
                'collection_number':row[6],'collection_category':row[7],
                'data_type':row[8],
                'wrs_path':row[9],'wrs_row':row[10],
                'cloud_cover':row[11],
                'north_lat':row[12],'south_lat':row[13],'west_lon':row[14],'east_lon':row[15],
                'total_size':row[16],'base_url':url}

            count += 1

        self.log.info('Query found that %d new files were added in the past %d day(s).' % (count,n))
        return(url_list)
