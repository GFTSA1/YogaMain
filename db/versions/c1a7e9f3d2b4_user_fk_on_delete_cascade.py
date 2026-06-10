"""add ON DELETE CASCADE to user_id foreign keys

Revision ID: c1a7e9f3d2b4
Revises: efbb6e7b5422
Create Date: 2026-06-10 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "c1a7e9f3d2b4"
down_revision: Union[str, Sequence[str], None] = "efbb6e7b5422"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# (table, constraint_name, local_col) for every FK pointing at user.id that
# should cascade when a user is deleted. The original constraints were created
# without explicit names, so Postgres auto-named them "<table>_<col>_fkey".
_FKS = (
    ("refreshtoken", "refreshtoken_user_id_fkey", "user_id"),
    ("usertrip", "usertrip_user_id_fkey", "user_id"),
    ("useryogacourse", "useryogacourse_user_id_fkey", "user_id"),
    ("grouptrainingstudiouser", "grouptrainingstudiouser_user_id_fkey", "user_id"),
)


def upgrade() -> None:
    """Recreate each user_id FK with ON DELETE CASCADE."""
    for table, name, col in _FKS:
        op.drop_constraint(name, table, type_="foreignkey")
        op.create_foreign_key(
            name, table, "user", [col], ["id"], ondelete="CASCADE"
        )


def downgrade() -> None:
    """Recreate each user_id FK without ON DELETE CASCADE."""
    for table, name, col in _FKS:
        op.drop_constraint(name, table, type_="foreignkey")
        op.create_foreign_key(name, table, "user", [col], ["id"])
