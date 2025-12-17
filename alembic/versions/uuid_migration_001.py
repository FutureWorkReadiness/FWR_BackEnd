"""Initial database schema with UUID primary keys

Creates all tables with:
- UUID primary keys (e.g., user_id, quiz_id, sector_id)
- Proper foreign key relationships
- Timestamps (created_at, updated_at)

Revision ID: uuid_migration_001
Revises: None (initial migration)
Create Date: 2024-01-15

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'uuid_migration_001'
down_revision = None  # Initial migration
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Create all tables with UUID primary keys.
    """
    # Create sectors table with UUID
    op.create_table('sectors',
        sa.Column('sector_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('sector_id'),
        sa.UniqueConstraint('name')
    )
    op.create_index('ix_sectors_sector_id', 'sectors', ['sector_id'], unique=False)
    op.create_index('ix_sectors_name', 'sectors', ['name'], unique=False)
    
    # Create branches table with UUID
    op.create_table('branches',
        sa.Column('branch_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('sector_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['sector_id'], ['sectors.sector_id'], ),
        sa.PrimaryKeyConstraint('branch_id')
    )
    op.create_index('ix_branches_branch_id', 'branches', ['branch_id'], unique=False)
    op.create_index('ix_branches_name', 'branches', ['name'], unique=False)
    
    # Create specializations table with UUID
    op.create_table('specializations',
        sa.Column('specialization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('branch_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['branch_id'], ['branches.branch_id'], ),
        sa.PrimaryKeyConstraint('specialization_id')
    )
    op.create_index('ix_specializations_specialization_id', 'specializations', ['specialization_id'], unique=False)
    op.create_index('ix_specializations_name', 'specializations', ['name'], unique=False)
    
    # Create users table with UUID
    op.create_table('users',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('is_verified', sa.Boolean(), nullable=True, default=False),
        sa.Column('preferred_specialization_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('readiness_score', sa.Float(), nullable=True, default=0.0),
        sa.Column('technical_score', sa.Float(), nullable=True, default=0.0),
        sa.Column('soft_skills_score', sa.Float(), nullable=True, default=0.0),
        sa.Column('leadership_score', sa.Float(), nullable=True, default=0.0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['preferred_specialization_id'], ['specializations.specialization_id'], ),
        sa.PrimaryKeyConstraint('user_id'),
        sa.UniqueConstraint('email')
    )
    op.create_index('ix_users_user_id', 'users', ['user_id'], unique=False)
    op.create_index('ix_users_email', 'users', ['email'], unique=False)
    
    # Create badges table with UUID
    op.create_table('badges',
        sa.Column('badge_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('criteria', sa.Text(), nullable=False),
        sa.Column('icon_url', sa.String(length=500), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('required_score', sa.Float(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('badge_id'),
        sa.UniqueConstraint('name')
    )
    op.create_index('ix_badges_badge_id', 'badges', ['badge_id'], unique=False)
    
    # Create quizzes table with UUID
    op.create_table('quizzes',
        sa.Column('quiz_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('specialization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('difficulty_level', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('time_limit_minutes', sa.Integer(), nullable=True, default=30),
        sa.Column('passing_score', sa.Float(), nullable=True, default=70.0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['specialization_id'], ['specializations.specialization_id'], ),
        sa.PrimaryKeyConstraint('quiz_id')
    )
    op.create_index('ix_quizzes_quiz_id', 'quizzes', ['quiz_id'], unique=False)
    
    # Create questions table with UUID
    op.create_table('questions',
        sa.Column('question_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('quiz_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('question_type', sa.String(length=50), nullable=False),
        sa.Column('points', sa.Integer(), nullable=True, default=1),
        sa.Column('order_index', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['quiz_id'], ['quizzes.quiz_id'], ),
        sa.PrimaryKeyConstraint('question_id')
    )
    op.create_index('ix_questions_question_id', 'questions', ['question_id'], unique=False)
    
    # Create question_options table with UUID
    op.create_table('question_options',
        sa.Column('option_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('question_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('option_text', sa.Text(), nullable=False),
        sa.Column('is_correct', sa.Boolean(), nullable=True, default=False),
        sa.Column('order_index', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['question_id'], ['questions.question_id'], ),
        sa.PrimaryKeyConstraint('option_id')
    )
    op.create_index('ix_question_options_option_id', 'question_options', ['option_id'], unique=False)
    
    # Create quiz_attempts table with UUID
    op.create_table('quiz_attempts',
        sa.Column('attempt_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('quiz_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('max_score', sa.Float(), nullable=False),
        sa.Column('percentage', sa.Float(), nullable=False),
        sa.Column('time_taken_minutes', sa.Integer(), nullable=True),
        sa.Column('is_passed', sa.Boolean(), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['quiz_id'], ['quizzes.quiz_id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('attempt_id')
    )
    op.create_index('ix_quiz_attempts_attempt_id', 'quiz_attempts', ['attempt_id'], unique=False)
    
    # Create goals table with UUID
    op.create_table('goals',
        sa.Column('goal_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('target_value', sa.Float(), nullable=False),
        sa.Column('current_value', sa.Float(), nullable=True, default=0.0),
        sa.Column('is_completed', sa.Boolean(), nullable=True, default=False),
        sa.Column('target_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('goal_id')
    )
    op.create_index('ix_goals_goal_id', 'goals', ['goal_id'], unique=False)
    
    # Create journal_entries table with UUID
    op.create_table('journal_entries',
        sa.Column('entry_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('prompt', sa.String(length=500), nullable=True),
        sa.Column('entry_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('entry_id')
    )
    op.create_index('ix_journal_entries_entry_id', 'journal_entries', ['entry_id'], unique=False)
    
    # Create user_badges table with UUID
    op.create_table('user_badges',
        sa.Column('user_badge_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('badge_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('earned_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('shared', sa.Boolean(), nullable=True, default=False),
        sa.ForeignKeyConstraint(['badge_id'], ['badges.badge_id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('user_badge_id'),
        sa.UniqueConstraint('user_id', 'badge_id', name='unique_user_badge')
    )
    op.create_index('ix_user_badges_user_badge_id', 'user_badges', ['user_badge_id'], unique=False)
    
    # Create peer_benchmarks table with UUID
    op.create_table('peer_benchmarks',
        sa.Column('benchmark_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('specialization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('avg_readiness_score', sa.Float(), nullable=False, default=0.0),
        sa.Column('avg_technical_score', sa.Float(), nullable=False, default=0.0),
        sa.Column('avg_soft_skills_score', sa.Float(), nullable=False, default=0.0),
        sa.Column('avg_leadership_score', sa.Float(), nullable=False, default=0.0),
        sa.Column('total_users', sa.Integer(), nullable=False, default=0),
        sa.Column('median_readiness_score', sa.Float(), nullable=False, default=0.0),
        sa.Column('common_strengths', sa.Text(), nullable=True),
        sa.Column('common_gaps', sa.Text(), nullable=True),
        sa.Column('last_updated', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['specialization_id'], ['specializations.specialization_id'], ),
        sa.PrimaryKeyConstraint('benchmark_id')
    )
    op.create_index('ix_peer_benchmarks_benchmark_id', 'peer_benchmarks', ['benchmark_id'], unique=False)


def downgrade() -> None:
    """
    This migration is not reversible without data loss.
    The downgrade will drop all tables.
    """
    bind = op.get_bind()
    
    tables_to_drop = [
        'peer_benchmarks', 'user_badges', 'journal_entries', 'goals',
        'quiz_attempts', 'question_options', 'questions', 'quizzes',
        'badges', 'users', 'specializations', 'branches', 'sectors'
    ]
    
    for table in tables_to_drop:
        bind.execute(sa.text(f'DROP TABLE IF EXISTS {table} CASCADE'))

