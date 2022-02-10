from rest_framework.exceptions import ErrorDetail

from common.exception_handler import add_error_codes


def test_error_codes():
    error_data = {
        'data': [ErrorDetail(string="Це поле обов'язкове.", code='required')],
        'signature': [ErrorDetail(string="Це поле обов'язкове.", code='required')]
    }

    errors_with_error_codes = add_error_codes(error_data)

    data = errors_with_error_codes.get('data', [])
    assert len(data) == 1
    assert data[0].get('code')
    assert data[0].get('description')

    signature = errors_with_error_codes.get('signature', [])
    assert len(signature) == 1
    assert signature[0].get('code')
    assert signature[0].get('description')
