from tortoise import fields, models

class ModelName(models.Model):
    name = fields.CharField(
        max_length=20
    )