import logging

from rest_framework.exceptions import ErrorDetail
from rest_framework.views import exception_handler as drf_exception_handler

from fs_cabinet.settings import DEFAULT_LOGGER_NAME

logger = logging.getLogger(DEFAULT_LOGGER_NAME)


def exception_handler(exception, context):
    logger.info(f'exception: {exception}')
    logger.info(f'context: {context}')
    response = drf_exception_handler(exception, context)
    logger.info(f'response: {response}')

    if response is not None:
        response.data = add_error_codes(response.data)

    logger.info(f'transformed to: {response.data}')
    return response


# TODO: test with
# {'data': [ErrorDetail(string="Це поле обов'язкове.", code='required')], 'signature': [ErrorDetail(string="Це поле обов'язкове.", code='required')]}
# and other types
def add_error_codes(errors_dict):
    collected_errors = {}

    for field, errors in errors_dict.items():

        if isinstance(errors, ErrorDetail):
            collected_errors[field] = {'code': errors.code, 'description': str(errors)}
            continue

        if isinstance(errors, dict):
            collected_errors[field] = errors
            collected_errors[field].update(add_error_codes(errors))
            continue

        if isinstance(errors, list):
            collected_errors[field] = []

            for error in errors:

                if isinstance(error, dict):
                    collected_errors[field].append(add_error_codes(error))
                    continue

                if isinstance(error, ErrorDetail):
                    collected_errors[field].append({'code': error.code, 'description': str(error)})
                    continue

            continue

        logger.error(f'Unknown error type {type(error)} {error}')

    return collected_errors
