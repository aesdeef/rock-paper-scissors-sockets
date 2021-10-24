from tortoise import fields, models


class DummyModel(models.Model):
    text = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)

    def __str__(self):
        return self.text
