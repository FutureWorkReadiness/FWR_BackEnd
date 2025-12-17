#!/usr/bin/env python3
"""
Database seed runner script.
Run this script to manually seed the database with initial data.

Usage:
    python seed_database.py           # Run all seeds (skip existing data)
    python seed_database.py --force   # Force re-seed (add missing data)
    python seed_database.py sectors   # Seed sectors only
    python seed_database.py quizzes   # Seed quizzes only
"""

import sys
import argparse


def main():
    parser = argparse.ArgumentParser(description="Seed the database with initial data")
    parser.add_argument(
        "target",
        nargs="?",
        default="all",
        choices=["all", "sectors", "quizzes", "expanded"],
        help="What to seed (default: all)",
    )
    parser.add_argument("--force", action="store_true", help="Force seeding even if data exists")

    args = parser.parse_args()

    print("=" * 50)
    print("🌱 FWR Database Seeder")
    print("=" * 50)

    if args.target == "all":
        from seeds.base import run_all_seeds

        run_all_seeds(force=args.force)

    elif args.target == "sectors":
        from seeds.seed_sectors import seed_sectors

        seed_sectors(force=args.force)

    elif args.target == "quizzes":
        from seeds.seed_quizzes import seed_quizzes

        seed_quizzes(force=args.force)

    elif args.target == "expanded":
        from seeds.seed_quizzes import seed_expanded_quizzes

        seed_expanded_quizzes()

    print("=" * 50)


if __name__ == "__main__":
    main()
