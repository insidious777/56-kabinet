from decimal import Decimal

from django.core.validators import MinValueValidator, DecimalValidator
from django.db import models
from django.utils.translation import gettext_lazy as _, pgettext_lazy, gettext
from imagekit.models import ProcessedImageField
from pilkit.processors import ResizeToFill, Anchor

from common.utils import get_local_now


class MenuCategory(models.Model):
    icon = ProcessedImageField(verbose_name=_('Icon'),
                               upload_to='menu_category_icons',
                               processors=[ResizeToFill(width=40, height=40, upscale=True, anchor=Anchor.CENTER)],
                               format='PNG',
                               options={'quality': 100})
    name = models.CharField(verbose_name=pgettext_lazy('Name', 'Category name'), max_length=100, help_text=_('Shows in miniatures'))
    title = models.CharField(verbose_name=_('Title'), max_length=100, help_text=_('Shows in sections on the page'))

    show = models.BooleanField(verbose_name=_('Show'), default=True)
    order_index = models.PositiveSmallIntegerField(verbose_name=_('Order index'), null=True, blank=True)

    from_time = models.TimeField(verbose_name=_('From time'), null=True, blank=True)
    to_time = models.TimeField(verbose_name=_('To time'), null=True, blank=True)

    can_order = models.BooleanField(verbose_name=_('Can order'), default=True)

    created_at = models.DateTimeField(verbose_name=_('Created at'), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_('Updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Menu category')
        verbose_name_plural = _('Menu categories')

    def __str__(self):
        return gettext('Category %(category_name)s') % {'category_name': self.name}

    def get_menu_items_to_show(self):
        return self.menu_items.filter(show=True)

    def has_time_restriction(self):
        return any([
            self.from_time,
            self.to_time
        ])

    def can_order_now(self):
        can_order = True

        if self.has_time_restriction():
            now_time = get_local_now().time()
            can_order = True

            if self.from_time:
                can_order = can_order and (self.from_time < now_time)

            if self.to_time:
                can_order = can_order and (now_time < self.to_time)

        return can_order


class Addition(models.Model):
    title = models.CharField(verbose_name=_('Title'), max_length=100)
    price = models.DecimalField(verbose_name=_('Price'), max_digits=6, decimal_places=0, validators=[MinValueValidator(Decimal('0.00')), DecimalValidator(max_digits=6, decimal_places=0)])
    show = models.BooleanField(verbose_name=_('Show'), default=True)

    created_at = models.DateTimeField(verbose_name=_('Created at'), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_('Updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Addition')
        verbose_name_plural = _('Additions')

    def __str__(self):
        return gettext('Addition "%(title)s"') % {'title': self.title}


class MenuItem(models.Model):
    image = ProcessedImageField(verbose_name=_('Image'),
                                upload_to='menu_images',
                                processors=[ResizeToFill(width=252, height=252, upscale=True, anchor=Anchor.CENTER)],
                                format='PNG',
                                options={'quality': 100})
    hq_image = ProcessedImageField(verbose_name=_('High quality image'),
                                   upload_to='hq_menu_images',
                                   processors=[ResizeToFill(width=1000, height=1000, upscale=True, anchor=Anchor.CENTER)],
                                   format='PNG',
                                   options={'quality': 100},
                                   null=True)
    title = models.CharField(verbose_name=_('Title'), max_length=100)
    price = models.DecimalField(verbose_name=_('Price'), max_digits=6, decimal_places=0, validators=[MinValueValidator(Decimal('0.00')), DecimalValidator(max_digits=6, decimal_places=0)])
    category = models.ForeignKey(MenuCategory, verbose_name=_('Category'), related_name='menu_items', null=True, blank=True, on_delete=models.SET_NULL)

    possible_additions = models.ManyToManyField(Addition, verbose_name=_('Possible additions'), related_name='purpose_menu_items', blank=True, help_text=_("Hold down \"Control\", or \"Command\" on a Mac, to select more than one."))

    volume = models.CharField(verbose_name=_('Volume'), max_length=50, null=True, blank=True)
    description = models.TextField(verbose_name=_('Description'), null=True, blank=True)
    show = models.BooleanField(verbose_name=_('Show'), default=True)

    created_at = models.DateTimeField(verbose_name=_('Created at'), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_('Updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Menu item')
        verbose_name_plural = _('Menu items')

    def __str__(self):
        if self.volume:
            return gettext('Menu item "%(menu_item_title)s %(menu_item_volume)s"') % {
                'menu_item_title': self.title,
                'menu_item_volume': self.volume,
            }

        return gettext('Menu item "%(menu_item_title)s"') % {'menu_item_title': self.title}


class Action(models.Model):
    name = models.CharField(verbose_name=_('Name'), max_length=100, default='')
    image = ProcessedImageField(verbose_name=_('Image'),
                                upload_to='action_images',
                                processors=[ResizeToFill(width=530, height=340, upscale=True, anchor=Anchor.CENTER)],
                                format='PNG',
                                options={'quality': 100})
    show = models.BooleanField(verbose_name=_('Show'), default=True)

    order_index = models.PositiveSmallIntegerField(verbose_name=_('Order index'), null=True, blank=True)

    created_at = models.DateTimeField(verbose_name=_('Created at'), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_('Updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Action')
        verbose_name_plural = _('Actions')

    def __str__(self):
        return gettext('Action "%(name)s"') % {'name': self.name or self.id}
