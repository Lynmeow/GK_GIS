from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webgis', '0006_siteconfig'),
    ]

    operations = [
        migrations.CreateModel(
            name='ResearchApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=200, verbose_name='Họ và tên')),
                ('email', models.EmailField(verbose_name='Email')),
                ('institution', models.CharField(max_length=300, verbose_name='Trường/Cơ quan')),
                ('purpose', models.TextField(verbose_name='Mục đích nghiên cứu')),
                ('status', models.CharField(
                    choices=[('pending', 'Chờ xét duyệt'), ('approved', 'Đã duyệt'), ('rejected', 'Từ chối')],
                    default='pending', max_length=20,
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('admin_note', models.TextField(blank=True, verbose_name='Ghi chú admin')),
            ],
            options={
                'verbose_name': 'Đơn nghiên cứu sinh',
                'db_table': 'research_applications',
                'ordering': ['-created_at'],
            },
        ),
    ]
