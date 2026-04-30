from typing import Sequence, Union
from alembic import op
from sqlalchemy import func

revision: str = "44ccba6b72e1"
down_revision: Union[str, Sequence[str], None] = "36909565aa15"  # последняя миграция перед этой
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('users', 'created_at', server_default=func.now())


def downgrade() -> None:
    op.alter_column('users', 'created_at', server_default=None)