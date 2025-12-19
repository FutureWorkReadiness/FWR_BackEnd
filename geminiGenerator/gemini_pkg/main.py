"""
Gemini Quiz Generator - Main Entry Point

Usage:
    python -m gemini_pkg.main                                    # Generate all sectors
    python -m gemini_pkg.main --sector technology                # Generate one sector only
    python -m gemini_pkg.main --test                             # Test single career/level
    python -m gemini_pkg.main --test --soft-skills               # Test soft skills only
    python -m gemini_pkg.main --status                           # Show checkpoint status
"""

import logging
import sys
import argparse
import os

# Environment variables are injected by Docker - no file-based loading needed
# os.getenv() will read from the environment directly

from gemini_pkg.config.settings import ensure_dirs, load_checkpoint, RESULTS_LOGS_DIR
from gemini_pkg.services.generator import GeminiQuizGeneratorV4


def setup_logging(verbose: bool = False):
    """Configure logging for the application."""
    level = logging.DEBUG if verbose else logging.INFO

    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    # File handler
    ensure_dirs()
    file_handler = logging.FileHandler(
        f"{RESULTS_LOGS_DIR}/generation.log",
        mode="a",
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.handlers = []  # Clear existing handlers
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # Reduce noise from HTTP libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def main():
    parser = argparse.ArgumentParser(
        description="Generate interview questions using Gemini API"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run a test generation for a single career/level",
    )
    parser.add_argument(
        "--sector",
        type=str,
        default=None,
        help="Run only this sector (e.g., technology, finance, health_social_care, education)",
    )
    parser.add_argument(
        "--career",
        type=str,
        default="FRONTEND_DEVELOPER",
        help="Career for test mode (default: FRONTEND_DEVELOPER)",
    )
    parser.add_argument(
        "--level",
        type=int,
        default=1,
        help="Level for test mode (default: 1)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose/debug logging",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show checkpoint status and exit",
    )
    parser.add_argument(
        "--soft-skills",
        action="store_true",
        help="Generate soft skills questions (use with --test for test mode)",
    )

    args = parser.parse_args()

    setup_logging(verbose=args.verbose)

    # Show status and exit if requested
    if args.status:
        checkpoint = load_checkpoint()
        if not checkpoint:
            print("No checkpoint found. No previous runs.")
        else:
            completed = [k for k, v in checkpoint.items() if v == "done"]
            print(f"Checkpoint found with {len(completed)} completed chunks:")
            for chunk in sorted(completed)[:20]:
                print(f"  ✓ {chunk}")
            if len(completed) > 20:
                print(f"  ... and {len(completed) - 20} more")
        return 0

    logging.info("=" * 60)
    logging.info("🚀 Starting Gemini Quiz Generator V4")
    logging.info("=" * 60)

    try:
        generator = GeminiQuizGeneratorV4()

        if args.test:
            # Test mode: single career/level or soft skills
            if args.soft_skills:
                logging.info("🧠 Test mode: Soft skills questions")
                generator.generate_soft_skills_block()
            else:
                sector = args.sector or "technology"
                logging.info(f"📝 Test mode: {sector}/{args.career} Level {args.level}")
                generator.generate_for_career_level(
                    sector,
                    args.career,
                    args.level,
                )
                # Also save production data output for testing 
                # generator._save_sector_production_data(sector)
        elif args.sector:
            # Single sector mode
            logging.info(f"📝 Single sector mode: {args.sector}")
            generator.generate_sector(args.sector)
        elif args.soft_skills:
            # Soft skills only mode
            logging.info("🧠 Generating soft skills questions only")
            generator.generate_soft_skills_block()
        else:
            # Full generation mode
            logging.info("📝 Full generation mode (all sectors)")
            generator.generate_all()

        logging.info("=" * 60)
        logging.info("✅ Generation complete!")
        logging.info("=" * 60)
        return 0

    except EnvironmentError as e:
        logging.error(f"❌ Environment error: {e}")
        logging.error("Make sure GEMINI_API_KEY is set in your .env file")
        return 1
    except KeyboardInterrupt:
        logging.warning("\n🛑 Interrupted by user")
        return 130
    except Exception as e:
        logging.exception(f"❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
