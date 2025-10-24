import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('projects', '0006_prepare_fk_for_uuid'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                -- КРОК 1: Видалити всі FK constraints
                DO $$
                DECLARE
                    constraint_record RECORD;
                BEGIN
                    FOR constraint_record IN
                        SELECT conname, conrelid::regclass AS table_name
                        FROM pg_constraint
                        WHERE confrelid = 'projects_project'::regclass
                        AND contype = 'f'
                    LOOP
                        EXECUTE format('ALTER TABLE %s DROP CONSTRAINT %I CASCADE',
                                     constraint_record.table_name,
                                     constraint_record.conname);
                    END LOOP;
                END $$;

                -- КРОК 2: Видалити старі FK колонки project_id (integer)
                ALTER TABLE projects_projectattachment DROP COLUMN IF EXISTS project_id CASCADE;
                ALTER TABLE projects_projectaudit DROP COLUMN IF EXISTS project_id CASCADE;

                -- КРОК 3: Замінити Project ID
                ALTER TABLE projects_project DROP CONSTRAINT projects_project_pkey CASCADE;
                ALTER TABLE projects_project DROP COLUMN id;
                ALTER TABLE projects_project RENAME COLUMN uuid TO id;
                ALTER TABLE projects_project ADD PRIMARY KEY (id);

                -- КРОК 4: Замінити ProjectAttachment ID
                ALTER TABLE projects_projectattachment DROP CONSTRAINT IF EXISTS projects_projectattachment_pkey CASCADE;
                ALTER TABLE projects_projectattachment DROP COLUMN id;
                ALTER TABLE projects_projectattachment RENAME COLUMN uuid TO id;
                ALTER TABLE projects_projectattachment ADD PRIMARY KEY (id);

                -- КРОК 5: Замінити ProjectAudit ID
                ALTER TABLE projects_projectaudit DROP CONSTRAINT IF EXISTS projects_projectaudit_pkey CASCADE;
                ALTER TABLE projects_projectaudit DROP COLUMN id;
                ALTER TABLE projects_projectaudit RENAME COLUMN uuid TO id;
                ALTER TABLE projects_projectaudit ADD PRIMARY KEY (id);

                -- КРОК 6: Тепер можна перейменувати project_uuid -> project_id
                ALTER TABLE projects_projectattachment RENAME COLUMN project_uuid TO project_id;
                ALTER TABLE projects_projectaudit RENAME COLUMN project_uuid TO project_id;

                -- КРОК 7: Додати FK constraints
                ALTER TABLE projects_projectattachment
                ADD CONSTRAINT projects_projectattachment_project_fk
                FOREIGN KEY (project_id) REFERENCES projects_project(id) ON DELETE CASCADE;

                ALTER TABLE projects_projectaudit
                ADD CONSTRAINT projects_projectaudit_project_fk
                FOREIGN KEY (project_id) REFERENCES projects_project(id) ON DELETE CASCADE;
            """,
            reverse_sql="SELECT 1;",
        ),
    ]
