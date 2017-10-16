from google.cloud import bigquery
import uuid

class Query():

    def __init__(self):
        self.client = bigquery.Client.from_service_account_json('service_account.json')
        return

    def find_week_old(self):
        '''
            Queries Google BigQuery to get urls from TIFFS uploaded within the last week.
            Returns URLS
        '''
        query_job = self.client.run_async_query(str(uuid.uuid4()), """

            SELECT *
            FROM
              [bigquery-public-data:cloud_storage_geo_index.landsat_index] a
            WHERE
              TIMESTAMP(date(a.date_acquired)) > DATE_ADD(USEC_TO_TIMESTAMP(NOW()), -1, 'WEEK');

            """)
        print("STARTING QUERY")
        query_job.begin()
        query_job.result()
        destination_table = query_job.destination
        destination_table.reload()
        count = 0
        url_list = []
        for row in destination_table.fetch_data():
            # brutish, but it gets what we need. row[17] corresponds to the URL column of the row for this SQL request
            url = row[17]
            url_list.append(url)
            count += 1

        print(count, " new TIFFS added in the past week.")

        return(url_list)
