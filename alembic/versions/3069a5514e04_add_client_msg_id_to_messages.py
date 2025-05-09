"""add client_msg_id to messages

Revision ID: 3069a5514e04
Revises: 9b22a23d7be5
Create Date: 2025-04-18 09:01:20.538695

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3069a5514e04'
down_revision: Union[str, None] = '9b22a23d7be5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('messages', sa.Column('client_msg_id', sa.String(length=36), nullable=True))
    op.create_index(op.f('ix_messages_client_msg_id'), 'messages', ['client_msg_id'], unique=False)
    op.create_unique_constraint('unique_chat_client_msg', 'messages', ['chat_id', 'client_msg_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('unique_chat_client_msg', 'messages', type_='unique')
    op.drop_index(op.f('ix_messages_client_msg_id'), table_name='messages')
    op.drop_column('messages', 'client_msg_id')
    # ### end Alembic commands ###
