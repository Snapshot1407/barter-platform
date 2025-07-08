from rest_framework import serializers
from .models import Ad, ExchangeProposal
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class AdSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)  # Только для чтения

    class Meta:
        model = Ad
        fields = ['id', 'user',
                  'title', 'description',
                  'image_url', 'category',
                  'condition', 'created_at',]
                  # 'status',]
        read_only_fields = ['id', 'user', 'created_at']  # Автозаполняемые поля


class AdCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ad
        fields = [
            'id','title', 'description', 'image_url',
            'category', 'condition'
        ]
        read_only_fields = ['id']


class ProposalSerializer(serializers.ModelSerializer):
    ad_sender = AdSerializer(read_only=True)
    ad_receiver = AdSerializer(read_only=True)

    class Meta:
        model = ExchangeProposal
        fields = ['id', 'ad_sender', 'ad_receiver', 'comment', 'status', 'created_at']
        read_only_fields = ['id', 'status', 'created_at']

class ProposalCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeProposal
        fields = ['ad_sender', 'ad_receiver', 'comment']
        extra_kwargs = {
            'ad_sender': {'required': True},
            'ad_receiver': {'required': True}
        }

    def validate(self, data):
        """
        Проверяет, что товар не предлагается для обмена сам на себя
        """
        ad_sender = self.context.get('ad_sender')
        ad_receiver = data.get('ad_receiver')

        if ad_sender and ad_receiver and ad_sender.id == ad_receiver.id:
            raise serializers.ValidationError("Нельзя предлагать обмен товара на самого себя")

        return data

    def create(self, validated_data):
        # Убедимся, что отправитель - текущий пользователь
        request = self.context.get('request')
        if validated_data['ad_sender'].user != request.user:
            raise serializers.ValidationError({
                'ad_sender': ['Вы не являетесь владельцем объявления-отправителя']
            })

        return ExchangeProposal.objects.create(**validated_data)

class ProposalUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeProposal
        fields = ['status']

    def validate_status(self, value):
        """
        Валидация статуса предложения
        """
        valid_statuses = [choice[0] for choice in ExchangeProposal.STATUS_CHOICES]
        if value not in valid_statuses:
            raise serializers.ValidationError(
                f"Недопустимый статус. Допустимые значения: {', '.join(valid_statuses)}"
            )

        # Дополнительная проверка, что нельзя изменить статус на PENDING
        if value == 'PENDING':
            raise serializers.ValidationError(
                "Нельзя изменить статус обратно на 'ожидание'"
            )

        return value
