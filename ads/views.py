from django.views.generic import CreateView, UpdateView
from .forms import AdForm
from drf_spectacular.utils import extend_schema_view, extend_schema
from django.core.paginator import Paginator
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, BasePermission
from django.shortcuts import get_object_or_404
from .models import Ad, ExchangeProposal
from .serializers import (
    AdSerializer,
    AdCreateUpdateSerializer,
    ProposalSerializer,
    ProposalCreateSerializer,
    ProposalUpdateSerializer
)


class AdCreateView(CreateView):
    model = Ad
    form_class = AdForm
    template_name = 'ads/ad_form.html'
    success_url = '/ads/'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Разрешаем GET, HEAD, OPTIONS запросы
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True

        # Разрешаем изменение только владельцу
        return obj.user == request.user


@extend_schema_view(
    list=extend_schema(description="Получить список всех объявлений"),
    create=extend_schema(description="Создать новое объявление"),
)

class AdViewSet(viewsets.ModelViewSet):
    queryset = Ad.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'title']
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {"error": "Требуется аутентификация!"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().create(request, *args, **kwargs)

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]  # Только для авторизованных
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return AdCreateUpdateSerializer
        return AdSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)# Автоматическое сохранение текущего пользователя

    @action(detail=False, methods=['GET'])
    def search(self, request):
        """Расширенный поиск с фильтрацией"""
        queryset = self.filter_queryset(self.get_queryset())

        # Фильтрация по категории
        category = request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)

        # Фильтрация по состоянию
        condition = request.query_params.get('condition')
        if condition:
            queryset = queryset.filter(condition=condition)

        # Пагинация
        page = request.query_params.get('page', 1)
        paginator = Paginator(queryset, 10)
        serializer = self.get_serializer(paginator.page(page), many=True)

        return Response({
            'count': paginator.count,
            'results': serializer.data
        })

    def destroy(self, request, *args, **kwargs):
        """Удаление с проверкой авторства"""
        instance = self.get_object()
        if instance.user != request.user:
            return Response(
                {"error": "Вы не можете удалить чужое объявление"},
                status=status.HTTP_403_FORBIDDEN
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response(
                {"detail": "У вас нет прав для выполнения этого действия."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

class ProposalViewSet(viewsets.ModelViewSet):
    queryset = ExchangeProposal.objects.all()
    serializer_class = ProposalSerializer

    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return ProposalCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ProposalUpdateSerializer
        return ProposalSerializer

    def get_queryset(self):
        """Фильтрация предложений по отправителю/получателю/статусу"""
        queryset = super().get_queryset()

        # Фильтрация для отправителя
        if 'sender' in self.request.query_params:
            queryset = queryset.filter(
                ad_sender__user=self.request.user,
                ad_sender_id=self.request.query_params['sender']
            )

        # Фильтрация для получателя
        if 'receiver' in self.request.query_params:
            queryset = queryset.filter(
                ad_receiver__user=self.request.user,
                ad_receiver_id=self.request.query_params['receiver']
            )

        # Фильтрация по статусу
        if 'status' in self.request.query_params:
            queryset = queryset.filter(
                status=self.request.query_params['status']
            )

        return queryset

    def create(self, request, *args, **kwargs):
        # Получаем ID объявления отправителя и получателя из запроса
        sender_ad_id = request.data.get('ad_sender')
        receiver_ad_id = request.data.get('ad_receiver')

        # Проверяем наличие обязательных полей
        if not sender_ad_id or not receiver_ad_id:
            return Response(
                {"error": "Необходимо указать ad_sender и ad_receiver"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Получаем объявления с проверкой прав доступа
        try:
            sender_ad = get_object_or_404(Ad, id=sender_ad_id)
            receiver_ad = get_object_or_404(Ad, id=receiver_ad_id)
        except Exception as e:
            return Response(
                {"error": "Одно из объявлений не найдено"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Проверка что отправитель - владелец объявления
        if sender_ad.user != request.user:
            return Response(
                {"error": "Вы не являетесь владельцем объявления-отправителя"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Защита от самобмена
        if sender_ad_id == receiver_ad_id:
            raise ValidationError("Нельзя предлагать обмен с самим собой")

        # Проверка что получатель не текущий пользователь (опционально)
        if receiver_ad.user == request.user:
            raise ValidationError("Нельзя предлагать обмен самому себе")

        # Проверка что такого предложения еще не существует
        if ExchangeProposal.objects.filter(
                ad_sender=sender_ad,
                ad_receiver=receiver_ad,
                status='pending'
        ).exists():
            return Response(
                {"error": "Такое предложение уже существует"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Создаем предложение
        serializer = ProposalCreateSerializer(
            data=request.data,
            context={
                'request': request,
                'ad_sender': sender_ad,
                'ad_receiver': receiver_ad
            }
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['PATCH'])
    def update_status(self, request, pk=None):
        """Обновление статуса предложения"""
        proposal = self.get_object()

        # Проверка что текущий пользователь - владелец объявления-получателя
        if proposal.ad_receiver.user != request.user:
            return Response(
                {"error": "Вы не можете изменять это предложение"},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ProposalUpdateSerializer(
            proposal,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)