from rest_framework import serializers

from prestart.models import CheckList


class CheckListSerializer(serializers.Serializer):
    user = serializers.CharField(max_length=150)
    data = serializers.DictField(
        child=serializers.CharField(max_length=3)
    )

    def create(self, validated_data):
        # user = validated_data['user']
        data = validated_data['data']

        # user_instance = User.objects.get(username=user)
        checklist_instances = []
        for question_id, answer in data.items():
            # checklist_instances.append(CheckList(user=user_instance, question_id=int(question_id), answer=answer))
            checklist_instances.append(CheckList(question_id=int(question_id), answer=answer))

        CheckList.objects.bulk_create(checklist_instances)
        return validated_data
