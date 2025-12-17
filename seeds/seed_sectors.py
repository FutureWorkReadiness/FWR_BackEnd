"""
Seed sectors, branches, and specializations.
Loads data from data/sectors.json
"""

from seeds.base import load_json_file, get_db_session
from src.app.modules.sectors.models import Sector, Branch, Specialization


def seed_sectors(force: bool = False) -> None:
    """
    Seed sectors, branches, and specializations from JSON.

    Args:
        force: If True, will add missing data even if some sectors exist
    """
    db = get_db_session()

    try:
        # Check if sectors already exist
        existing_count = db.query(Sector).count()

        if existing_count > 0 and not force:
            print(f"✅ Sectors already seeded: {existing_count} sector(s) found")
            return

        # Load sectors from JSON
        data = load_json_file("sectors.json")
        if not data:
            print("❌ Could not load sectors.json")
            return

        sectors_data = data.get("sectors", [])
        if not sectors_data:
            print("⚠️  No sectors found in sectors.json")
            return

        print(f"📂 Seeding {len(sectors_data)} sector(s)...")

        added_sectors = 0
        added_branches = 0
        added_specializations = 0

        for sector_data in sectors_data:
            # Check if sector already exists
            existing_sector = db.query(Sector).filter(Sector.name == sector_data["name"]).first()

            if existing_sector:
                sector = existing_sector
                print(f"  ⏩ Sector '{sector.name}' already exists")
            else:
                # Create sector
                sector = Sector(name=sector_data["name"], description=sector_data.get("description", ""))
                db.add(sector)
                db.commit()
                db.refresh(sector)
                added_sectors += 1
                print(f"  ✅ Created sector: {sector.name}")

            # Process branches
            for branch_data in sector_data.get("branches", []):
                existing_branch = (
                    db.query(Branch)
                    .filter(Branch.name == branch_data["name"], Branch.sector_id == sector.sector_id)
                    .first()
                )

                if existing_branch:
                    branch = existing_branch
                else:
                    branch = Branch(
                        name=branch_data["name"],
                        description=branch_data.get("description", ""),
                        sector_id=sector.sector_id,
                    )
                    db.add(branch)
                    db.commit()
                    db.refresh(branch)
                    added_branches += 1

                # Process specializations
                for spec_data in branch_data.get("specializations", []):
                    existing_spec = (
                        db.query(Specialization)
                        .filter(Specialization.name == spec_data["name"], Specialization.branch_id == branch.branch_id)
                        .first()
                    )

                    if not existing_spec:
                        specialization = Specialization(
                            name=spec_data["name"],
                            description=spec_data.get("description", ""),
                            branch_id=branch.branch_id,
                        )
                        db.add(specialization)
                        added_specializations += 1

                db.commit()

        print(f"✅ Sector seeding complete!")
        print(f"   - Sectors added: {added_sectors}")
        print(f"   - Branches added: {added_branches}")
        print(f"   - Specializations added: {added_specializations}")

    except Exception as e:
        print(f"❌ Error seeding sectors: {e}")
        import traceback

        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_sectors(force=False)

