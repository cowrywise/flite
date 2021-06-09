"""Response messages sub-module."""

ERROR_MESSAGES = {
    'not_found': (
        '{}_not_found.',
        'Ensure the ID passed is of an existing {}.'),
    'repeated': (
        'repeated_values',
        'Ensure your {} is unique.'
    ),
    'incorrect_data': (
        'incorrect_data',
        'Ensure the data passed is correct.'
    ),
    'permission': (
        'permission_required',
        'You don\'t have permission to edit {}'
    )
}