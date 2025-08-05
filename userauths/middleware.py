# middleware/request_profiler.py

import time
from django.db import connection, reset_queries
from django.utils.deprecation import MiddlewareMixin


class RequestProfilerMiddleware(MiddlewareMixin):
    def process_request(self, request):
        reset_queries()
        request.start_time = time.time()
        request._body = request.body  # Store request body

    def process_response(self, request, response):
        total_time = time.time() - getattr(request, 'start_time', time.time())
        queries = connection.queries
        num_queries = len(queries)
        total_sql_time = sum(float(q['time']) for q in queries)

        try:
            request_body = getattr(request, '_body', b'').decode('utf-8', errors='replace')
        except Exception:
            request_body = 'Unable to decode request body.'

        try:
            response_body = getattr(response, 'content', b'').decode('utf-8', errors='replace')
        except Exception:
            response_body = 'Unable to decode response body.'

        # Log to file.txt
        with open('file.txt', 'a', encoding='utf-8') as f:
            f.write('\n' + '=' * 80 + '\n')
            f.write(f'Method: {request.method}\n')
            f.write(f'Path: {request.get_full_path()}\n')
            f.write(f'Total Time: {total_time:.3f}s\n')
            f.write(f'DB Queries: {num_queries}\n')
            f.write(f'SQL Time: {total_sql_time:.3f}s\n\n')

            f.write('SQL QUERIES:\n')
            for i, query in enumerate(queries, start=1):
                f.write(f"  {i}. [{query['time']}s] {query['sql']}\n")

            f.write('Request Headers:\n')
            for key, value in request.headers.items():
                f.write(f'  {key}: {value}\n')

            f.write(f'\nRequest Body:\n{request_body}\n\n')

            f.write(f'Response Status: {response.status_code}\n')
            f.write('Response Headers:\n')
            for key, value in response.items():
                f.write(f'  {key}: {value}\n')

            f.write(f'\nResponse Body:\n{response_body}\n')
            f.write('=' * 80 + '\n')

        return response
