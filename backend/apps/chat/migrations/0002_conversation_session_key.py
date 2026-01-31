# Generated manually — add session_key to Conversation for ownership tracking

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='conversation',
            name='session_key',
            field=models.CharField(
                blank=True,
                db_index=True,
                help_text='Session key of the user who started this conversation',
                max_length=40,
            ),
        ),
    ]
