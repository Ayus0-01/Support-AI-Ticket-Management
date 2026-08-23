from rest_framework import serializers


class CreateKnowledgeArticleSerializer(serializers.Serializer):

    title = serializers.CharField(
        max_length=300
    )

    slug = serializers.SlugField(
        max_length=200
    )

    category = serializers.CharField(
        max_length=100
    )

    sub_category = serializers.CharField(
        max_length=150
    )

    tags = serializers.ListField(
        child=serializers.CharField(
            max_length=100
        ),
        required=False,
        default=list
    )

    content = serializers.CharField(
        min_length=1
    )

    source_system = serializers.ChoiceField(
        choices=[
            "MANUAL",
            "CONFLUENCE",
            "SHAREPOINT",
            "UPLOAD",
        ],
        default="MANUAL"
    )

    source_url = serializers.URLField(
        required=False,
        allow_blank=True,
        allow_null=True
    )

    visible_to_departments = serializers.ListField(
        child=serializers.CharField(
            max_length=100
        ),
        required=False,
        default=list
    )

    is_internal_only = serializers.BooleanField(
        default=False
    )

class KnowledgeArticleListSerializer(
    serializers.Serializer
):
    id = serializers.CharField(
        source="_id"
    )

    slug = serializers.CharField()
    title = serializers.CharField()
    category = serializers.CharField()
    sub_category = serializers.CharField()
    tags = serializers.ListField()
    status = serializers.CharField()
    version = serializers.IntegerField()
    source_system = serializers.CharField()
    is_internal_only = serializers.BooleanField()
    chunk_count = serializers.IntegerField()
    indexed_version = serializers.IntegerField(
        allow_null=True
    )
    updated_at = serializers.DateTimeField()
    created_at = serializers.DateTimeField()