from django.db import models


class Branch(models.Model):
    """
    門市。目前只有門市名稱一個欄位。
    """

    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "門市"
        verbose_name_plural = "門市"
