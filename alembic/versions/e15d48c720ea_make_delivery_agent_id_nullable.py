"""make_delivery_agent_id_nullable

Revision ID: e15d48c720ea
Revises: c7e642db3f76
Create Date: 2025-05-30 13:10:41.057014

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
# revision identifiers, used by Alembic.
revision: str = 'e15d48c720ea'
down_revision: Union[str, None] = 'c7e642db3f76'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
def upgrade() -> None:
    # Make delivery_agent_id nullable
    op.alter_column('orders', 'delivery_agent_id', 
                   existing_type=sa.UUID(), 
                   nullable=True, 
                   schema='orders')
def downgrade() -> None:
    # Make delivery_agent_id non-nullable (reverse operation)
    op.alter_column('orders', 'delivery_agent_id', 
                   existing_type=sa.UUID(), 
                   nullable=False, 
                   schema='orders')
