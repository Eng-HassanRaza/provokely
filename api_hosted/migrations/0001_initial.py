# Generated migration for api_hosted app

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='APIUser',
            fields=[
                ('id', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('email', models.EmailField(db_index=True, max_length=254, unique=True)),
                ('auth_token', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('total_requests', models.IntegerField(default=0)),
                ('total_tokens_used', models.IntegerField(default=0)),
                ('total_cost', models.DecimalField(decimal_places=4, default=0, max_digits=10)),
            ],
            options={
                'db_table': 'api_users',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='UsageLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('action', models.CharField(help_text='API action performed', max_length=100)),
                ('tokens_used', models.IntegerField(default=0)),
                ('cost', models.DecimalField(decimal_places=4, default=0, max_digits=10)),
                ('model', models.CharField(default='gpt-4o-mini', max_length=50)),
                ('prompt_length', models.IntegerField(default=0, help_text='Character length of prompt')),
                ('api_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='usage_logs', to='api_hosted.apiuser')),
            ],
            options={
                'db_table': 'usage_logs',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.AddIndex(
            model_name='usagelog',
            index=models.Index(fields=['api_user', 'timestamp'], name='usage_logs_api_use_a7b8e1_idx'),
        ),
    ]

