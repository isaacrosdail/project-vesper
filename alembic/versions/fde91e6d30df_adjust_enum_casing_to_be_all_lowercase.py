"""adjust enum casing to be all lowercase

Revision ID: fde91e6d30df
Revises: f5e12167e6d6
Create Date: 2026-03-01 02:57:39.081179+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fde91e6d30df'
down_revision: Union[str, None] = 'f5e12167e6d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TABLE tasks ALTER COLUMN priority TYPE VARCHAR")
    op.execute("DROP TYPE priority_enum")
    op.execute("CREATE TYPE priority_enum AS ENUM ('low', 'medium', 'high')")
    op.execute("ALTER TABLE tasks ALTER COLUMN priority TYPE priority_enum USING LOWER(priority)::priority_enum")

    # unit_enum
    # drop defaults first
    op.execute("ALTER TABLE recipes ALTER COLUMN yields_units DROP DEFAULT")
    op.execute("ALTER TABLE recipe_ingredients ALTER COLUMN amount_units DROP DEFAULT")

    # swap to varchar to shuffle
    op.execute("ALTER TABLE products ALTER COLUMN unit_type TYPE VARCHAR")
    op.execute("ALTER TABLE recipes ALTER COLUMN yields_units TYPE VARCHAR")
    op.execute("ALTER TABLE recipe_ingredients ALTER COLUMN amount_units TYPE VARCHAR")
    op.execute("DROP TYPE unit_enum")
    op.execute("DROP TYPE unitenum")
    op.execute("CREATE TYPE unit_enum AS ENUM ('g', 'kg', 'oz', 'lb', 'ml', 'l', 'fl_oz', 'ea')")
    op.execute("ALTER TABLE products ALTER COLUMN unit_type TYPE unit_enum USING LOWER(unit_type)::unit_enum")
    op.execute("ALTER TABLE recipes ALTER COLUMN yields_units TYPE unit_enum USING LOWER(yields_units)::unit_enum")
    op.execute("ALTER TABLE recipe_ingredients ALTER COLUMN amount_units TYPE unit_enum USING LOWER(amount_units)::unit_enum")

    # re-set defaults
    op.execute("ALTER TABLE recipes ALTER COLUMN yields_units SET DEFAULT 'g'")
    op.execute("ALTER TABLE recipe_ingredients ALTER COLUMN amount_units SET DEFAULT 'g'")


    # difficulty_enum
    op.execute("ALTER TABLE leet_code_records ALTER COLUMN difficulty TYPE VARCHAR")
    op.execute("DROP TYPE difficulty_enum")
    op.execute("CREATE TYPE difficulty_enum AS ENUM ('easy', 'medium', 'hard')")
    op.execute("ALTER TABLE leet_code_records ALTER COLUMN difficulty TYPE difficulty_enum USING LOWER(difficulty)::difficulty_enum")

    # language_enum
    op.execute("ALTER TABLE leet_code_records ALTER COLUMN language TYPE VARCHAR")
    op.execute("DROP TYPE language_enum")
    op.execute("CREATE TYPE language_enum AS ENUM ('python', 'js', 'cpp', 'c', 'go')")
    op.execute("ALTER TABLE leet_code_records ALTER COLUMN language TYPE language_enum USING LOWER(language)::language_enum")
    
    # lcstatus_enum
    op.execute("ALTER TABLE leet_code_records ALTER COLUMN status TYPE VARCHAR")
    op.execute("DROP TYPE lcstatus_enum")
    op.execute("CREATE TYPE lcstatus_enum AS ENUM ('solved', 'attempted', 'reviewed')")
    op.execute("ALTER TABLE leet_code_records ALTER COLUMN status TYPE lcstatus_enum USING LOWER(status)::lcstatus_enum")
    
    # product_category_enum
    op.execute("ALTER TABLE products ALTER COLUMN category TYPE VARCHAR")
    op.execute("DROP TYPE product_category_enum")
    op.execute("CREATE TYPE product_category_enum AS ENUM ('fruits', 'vegetables', 'legumes', 'grains', 'bakery', 'dairy_eggs', 'meats', 'seafood', 'fats_oils', 'snacks', 'sweets', 'beverages', 'condiments_sauces', 'processed_convenience', 'supplements')")
    op.execute("ALTER TABLE products ALTER COLUMN category TYPE product_category_enum USING LOWER(category)::product_category_enum")
    
    # status_enum
    op.execute("ALTER TABLE habits ALTER COLUMN status TYPE VARCHAR")
    op.execute("DROP TYPE status_enum")
    op.execute("CREATE TYPE status_enum AS ENUM ('experimental', 'established')")
    op.execute("ALTER TABLE habits ALTER COLUMN status TYPE status_enum USING LOWER(status)::status_enum")

    # user_role_enum
    op.execute("ALTER TABLE users ALTER COLUMN role TYPE VARCHAR")
    op.execute("DROP TYPE user_role_enum")
    op.execute("CREATE TYPE user_role_enum AS ENUM ('user', 'admin', 'owner')")
    op.execute("ALTER TABLE users ALTER COLUMN role TYPE user_role_enum USING LOWER(role)::user_role_enum")



def downgrade() -> None:
    """Downgrade schema."""

    # priority_enum
    op.execute("ALTER TABLE tasks ALTER COLUMN priority TYPE VARCHAR")
    op.execute("DROP TYPE priority_enum")
    op.execute("CREATE TYPE priority_enum AS ENUM ('LOW', 'MEDIUM', 'HIGH')")
    op.execute("ALTER TABLE tasks ALTER COLUMN priority TYPE priority_enum USING UPPER(priority)::priority_enum")

    # unit_enum (adding back unitenum)

    op.execute("ALTER TABLE recipes ALTER COLUMN yields_units DROP DEFAULT")
    op.execute("ALTER TABLE recipe_ingredients ALTER COLUMN amount_units DROP DEFAULT")

    op.execute("ALTER TABLE products ALTER COLUMN unit_type TYPE VARCHAR")
    op.execute("ALTER TABLE recipes ALTER COLUMN yields_units TYPE VARCHAR")
    op.execute("ALTER TABLE recipe_ingredients ALTER COLUMN amount_units TYPE VARCHAR")
    op.execute("DROP TYPE unit_enum")
    op.execute("CREATE TYPE unitenum AS ENUM ('G', 'KG', 'OZ', 'LB', 'ML', 'L', 'FL_OZ', 'EA')")
    op.execute("CREATE TYPE unit_enum AS ENUM ('G', 'KG', 'OZ', 'LB', 'ML', 'L', 'FL_OZ', 'EA')")
    op.execute("ALTER TABLE products ALTER COLUMN unit_type TYPE unit_enum USING UPPER(unit_type)::unit_enum")
    op.execute("ALTER TABLE recipes ALTER COLUMN yields_units TYPE unitenum USING UPPER(yields_units)::unitenum")
    op.execute("ALTER TABLE recipe_ingredients ALTER COLUMN amount_units TYPE unitenum USING UPPER(amount_units)::unitenum")
    # re-set defaults
    op.execute("ALTER TABLE recipes ALTER COLUMN yields_units SET DEFAULT 'G'")
    op.execute("ALTER TABLE recipe_ingredients ALTER COLUMN amount_units SET DEFAULT 'G'")

    # difficulty_enum
    op.execute("ALTER TABLE leet_code_records ALTER COLUMN difficulty TYPE VARCHAR")
    op.execute("DROP TYPE difficulty_enum")
    op.execute("CREATE TYPE difficulty_enum AS ENUM ('EASY', 'MEDIUM', 'HARD')")
    op.execute("ALTER TABLE leet_code_records ALTER COLUMN difficulty TYPE difficulty_enum USING UPPER(difficulty)::difficulty_enum")

    # language_enum
    op.execute("ALTER TABLE leet_code_records ALTER COLUMN language TYPE VARCHAR")
    op.execute("DELETE FROM leet_code_records WHERE language = 'go'")
    op.execute("DROP TYPE language_enum")
    op.execute("CREATE TYPE language_enum AS ENUM ('PYTHON', 'JS', 'CPP', 'C')")
    op.execute("ALTER TABLE leet_code_records ALTER COLUMN language TYPE language_enum USING UPPER(language)::language_enum")

    # lcstatus_enum
    op.execute("ALTER TABLE leet_code_records ALTER COLUMN status TYPE VARCHAR")
    op.execute("DROP TYPE lcstatus_enum")
    op.execute("CREATE TYPE lcstatus_enum AS ENUM ('SOLVED', 'ATTEMPTED', 'REVIEWED')")
    op.execute("ALTER TABLE leet_code_records ALTER COLUMN status TYPE lcstatus_enum USING UPPER(status)::lcstatus_enum")

    # product_category_enum
    op.execute("ALTER TABLE products ALTER COLUMN category TYPE VARCHAR")
    op.execute("DROP TYPE product_category_enum")
    op.execute("CREATE TYPE product_category_enum AS ENUM ('FRUITS', 'VEGETABLES', 'LEGUMES', 'GRAINS', 'BAKERY', 'DAIRY_EGGS', 'MEATS', 'SEAFOOD', 'FATS_OILS', 'SNACKS', 'SWEETS', 'BEVERAGES', 'CONDIMENTS_SAUCES', 'PROCESSED_CONVENIENCE', 'SUPPLEMENTS')")
    op.execute("ALTER TABLE products ALTER COLUMN category TYPE product_category_enum USING UPPER(category)::product_category_enum")

    # status_enum
    op.execute("ALTER TABLE habits ALTER COLUMN status TYPE VARCHAR")
    op.execute("DROP TYPE status_enum")
    op.execute("CREATE TYPE status_enum AS ENUM ('EXPERIMENTAL', 'ESTABLISHED')")
    op.execute("ALTER TABLE habits ALTER COLUMN status TYPE status_enum USING UPPER(status)::status_enum")

    # user_role_enum
    op.execute("ALTER TABLE users ALTER COLUMN role TYPE VARCHAR")
    op.execute("DROP TYPE user_role_enum")
    op.execute("CREATE TYPE user_role_enum AS ENUM ('USER', 'ADMIN', 'OWNER')")
    op.execute("ALTER TABLE users ALTER COLUMN role TYPE user_role_enum USING UPPER(role)::user_role_enum")

