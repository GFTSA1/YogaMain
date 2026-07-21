"""add auth fields and refreshtoken

Revision ID: efbb6e7b5422
Revises: b5af3fa12a68
Create Date: 2026-05-11 16:00:46.232008

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'efbb6e7b5422'
down_revision: Union[str, Sequence[str], None] = 'b5af3fa12a68'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Alter user columns
    op.alter_column('user', 'last_name', existing_type=sa.String(), nullable=True)
    op.alter_column('user', 'mobile_number', existing_type=sa.String(), nullable=True)
    op.alter_column(
        'user',
        'role',
        existing_type=sa.String(),
        server_default='user',
        nullable=False,
    )

    # Add new auth columns to user
    op.add_column('user', sa.Column('password_hash', sa.String(), nullable=True))
    op.add_column('user', sa.Column('google_sub', sa.String(), nullable=True))
    op.create_index('ix_user_google_sub', 'user', ['google_sub'], unique=True)

    # Create refreshtoken table
    op.create_table(
        'refreshtoken',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('token_hash', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('issued_at', sa.DateTime(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('revoked_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token_hash'),
    )
    op.create_index('ix_refreshtoken_user_id', 'refreshtoken', ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop refreshtoken table and its index
    op.drop_index('ix_refreshtoken_user_id', table_name='refreshtoken')
    op.drop_table('refreshtoken')

    # Remove new user columns
    op.drop_index('ix_user_google_sub', table_name='user')
    op.drop_column('user', 'google_sub')
    op.drop_column('user', 'password_hash')

    # Revert user column alterations
    op.alter_column(
        'user',
        'role',
        existing_type=sa.String(),
        server_default=None,
        nullable=False,
    )
    op.alter_column('user', 'mobile_number', existing_type=sa.String(), nullable=False)
    op.alter_column('user', 'last_name', existing_type=sa.String(), nullable=False)
