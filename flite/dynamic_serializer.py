from rest_framework import serializers


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        exclude_fields = kwargs.pop("exclude", None)

        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)
        if exclude_fields is not None:
            exclude = set(exclude_fields)
            for field_name in exclude:
                # drop fields to exclude
                self.fields.pop(field_name)
