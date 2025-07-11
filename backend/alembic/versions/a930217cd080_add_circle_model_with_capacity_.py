"""Add Circle model with capacity constraints

Revision ID: a930217cd080
Revises: b37f99db0c0e
Create Date: 2025-06-08 17:57:43.654663

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a930217cd080'
down_revision: Union[str, None] = 'b37f99db0c0e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('circles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('facilitator_id', sa.Integer(), nullable=False),
    sa.Column('capacity_min', sa.Integer(), nullable=False),
    sa.Column('capacity_max', sa.Integer(), nullable=False),
    sa.Column('location_name', sa.String(length=200), nullable=True),
    sa.Column('location_address', sa.String(length=500), nullable=True),
    sa.Column('meeting_schedule', sa.JSON(), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['facilitator_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_circles_facilitator_id'), 'circles', ['facilitator_id'], unique=False)
    op.create_index(op.f('ix_circles_id'), 'circles', ['id'], unique=False)
    op.create_index(op.f('ix_circles_name'), 'circles', ['name'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_circles_name'), table_name='circles')
    op.drop_index(op.f('ix_circles_id'), table_name='circles')
    op.drop_index(op.f('ix_circles_facilitator_id'), table_name='circles')
    op.drop_table('circles')
    # ### end Alembic commands ###
