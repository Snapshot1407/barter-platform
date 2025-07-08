from django.db import models
from django.contrib.auth.models import User



class Ad(models.Model):
    CATEGORY_CHOICES = [
        ('BOOKS', 'Книги'),
        ('ELECTRONICS', 'Электроника'),
        ('CLOTHING', 'Одежда'),
        ('OTHER', 'Другое'),
    ]

    # Состояние товара
    CONDITION_CHOICES = [
        ('NEW', 'Новый'),
        ('USED', 'Б/у'),
        ('DEFECT', 'С дефектом'),
    ]

    # # Состояние карточки товара
    # STATUS_CHOICES = [
    #     ('ACTIVE', 'Активно'),
    #     ('CLOSED', 'Закрыто'),
    #     ('ARCHIVED', 'В архиве'),
    # ]
    #
    # status = models.CharField(
    #     max_length=20,
    #     choices=STATUS_CHOICES,
    #     default='ACTIVE',
    #     verbose_name='Статус объявления'
    # )

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    title = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    image_url = models.URLField(blank=True, null=True, verbose_name='Ссылка на изображение')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, verbose_name='Категория')
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, verbose_name='Состояние')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')


    def __str__(self):
        return f'{self.title} (Пользователь: {self.user.username})'

    class Meta:
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'
        ordering = ['-created_at']

class ExchangeProposal(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Ожидает'),
        ('ACCEPTED', 'Принята'),
        ('REJECTED', 'Отклонена'),
    ]

    ad_sender = models.ForeignKey(
        Ad,
        on_delete=models.CASCADE,
        related_name='sent_proposals',
        verbose_name='Предлагаемый товар (отправитель)'
    )
    ad_receiver = models.ForeignKey(
        Ad,
        on_delete=models.CASCADE,
        related_name='received_proposals',
        verbose_name='Запрашиваемый товар (получатель)'
    )
    comment = models.TextField(blank=True, verbose_name='Комментарий')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        verbose_name='Статус'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    def __str__(self):
        return f'Предложение #{self.id}: {self.ad_sender.title} → {self.ad_receiver.title}'

    class Meta:
        verbose_name = 'Предложение обмена'
        verbose_name_plural = 'Предложения обмена'
        ordering = ['-created_at']