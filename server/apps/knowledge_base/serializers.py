from rest_framework import serializers


class CreateKnowledgeArticleSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=300)
    slug = serializers.SlugField(max_length=200)
    category = serializers.CharField(max_length=100)
    sub_category = serializers.CharField(max_length=150)
    tags = serializers.ListField(child=serializers.CharField(max_length=100), required=False, default=list)
    content = serializers.CharField(min_length=1)
    source_system = serializers.ChoiceField(choices=["MANUAL", "CONFLUENCE", "SHAREPOINT", "UPLOAD"], default="MANUAL")
    source_url = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    visible_to_departments = serializers.ListField(child=serializers.CharField(max_length=100), required=False, default=list)
    is_internal_only = serializers.BooleanField(default=False)


class UpdateKnowledgeArticleSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=300, required=False)
    slug = serializers.SlugField(max_length=200, required=False)
    category = serializers.CharField(max_length=100, required=False)
    sub_category = serializers.CharField(max_length=150, required=False)
    tags = serializers.ListField(child=serializers.CharField(max_length=100), required=False)
    content = serializers.CharField(min_length=1, required=False)
    source_system = serializers.ChoiceField(choices=["MANUAL", "CONFLUENCE", "SHAREPOINT", "UPLOAD"], required=False)
    source_url = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    visible_to_departments = serializers.ListField(child=serializers.CharField(max_length=100), required=False)
    is_internal_only = serializers.BooleanField(required=False)
    change_note = serializers.CharField(max_length=500, required=False, allow_blank=True)

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError("At least one article field must be provided.")
        return attrs


class PublishKnowledgeArticleSerializer(serializers.Serializer):
    change_note = serializers.CharField(max_length=500, required=False, default="Published", allow_blank=True)


class PreviewChunksSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=300, required=False, default="Preview")
    content = serializers.CharField(min_length=1)


class KnowledgeSearchSerializer(serializers.Serializer):
    query = serializers.CharField(min_length=1, max_length=2000)
    limit = serializers.IntegerField(min_value=1, max_value=100, required=False, default=10)
    top_k = serializers.IntegerField(min_value=1, max_value=20, required=False, default=5)
    category = serializers.CharField(max_length=100, required=False, allow_blank=True, allow_null=True)
    department = serializers.CharField(max_length=100, required=False, allow_blank=True, allow_null=True)
    include_internal = serializers.BooleanField(required=False, default=False)


class IngestionRequestSerializer(serializers.Serializer):
    paths = serializers.ListField(child=serializers.CharField(min_length=1), min_length=1, max_length=500)
    job_type = serializers.ChoiceField(choices=["BULK_UPLOAD", "CONFLUENCE_SYNC", "REINDEX"], required=False, default="BULK_UPLOAD")
    source_ref = serializers.CharField(required=False, allow_blank=True, default="")
    source_metadata = serializers.DictField(required=False, default=dict)


class KnowledgeArticleListSerializer(serializers.Serializer):
    id = serializers.CharField(source="_id")
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
    indexed_version = serializers.IntegerField(allow_null=True)
    embedding_model = serializers.CharField(allow_null=True, required=False)
    index_error = serializers.CharField(allow_null=True, required=False)
    updated_at = serializers.DateTimeField()
    created_at = serializers.DateTimeField()


class KnowledgeArticleDetailSerializer(KnowledgeArticleListSerializer):
    content = serializers.CharField()
    source_url = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    visible_to_departments = serializers.ListField(required=False)
    content_hash = serializers.CharField(required=False)
    last_indexed_at = serializers.DateTimeField(allow_null=True, required=False)
    author_id = serializers.CharField(required=False, allow_null=True)
    author_name = serializers.CharField(required=False)
    reviewed_by_id = serializers.CharField(required=False, allow_null=True)
    source_updated_at = serializers.DateTimeField(allow_null=True, required=False)


class ChunkPreviewSerializer(serializers.Serializer):
    index = serializers.IntegerField()
    heading_path = serializers.CharField(allow_blank=True)
    token_count = serializers.IntegerField()
    content = serializers.CharField()