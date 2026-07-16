"""
Husky CRM — 演示数据初始化脚本

运行后显示菜单，选择要执行的操作。
"""

import subprocess
import sys
from pathlib import Path

# 项目根目录
ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

DB_PATH = ROOT / "backend" / "huskycrm.db"


def run_sql(sql_file: str) -> None:
    """Execute a SQL file against the database."""
    sql_path = ROOT / sql_file
    if not sql_path.exists():
        print(f"[ERROR] SQL file not found: {sql_path}", file=sys.stderr)
        return
    result = subprocess.run(
        ["sqlite3", str(DB_PATH)],
        stdin=open(sql_path),
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"[ERROR] SQL execution failed: {result.stderr}", file=sys.stderr)
    else:
        print(f"[OK] Loaded {sql_file}")


async def init_tables():
    """1. 创建数据库表结构"""
    print("\n── 创建数据库表结构 ──")
    from app.database import init_db
    await init_db()
    print("[OK] Tables created")


async def seed_admin():
    """2. 创建管理员账号"""
    print("\n── 创建管理员账号 ──")
    from sqlalchemy import select
    from app.database import async_session
    from app.models.auth import User
    from app.core.security import hash_password

    async with async_session() as session:
        result = await session.execute(select(User).where(User.username == "admin"))
        if result.scalar_one_or_none():
            print("[SKIP] Admin user already exists (admin / admin123)")
            return
        admin = User(
            username="admin",
            email="admin@huskycrm.local",
            password_hash=hash_password("admin123"),
            display_name="Administrator",
            is_superuser=True,
        )
        session.add(admin)
        await session.commit()
        print("[OK] Created admin user (admin / admin123)")


async def seed_stages():
    """3. 创建销售阶段"""
    print("\n── 创建销售阶段 ──")
    from sqlalchemy import select
    from app.database import async_session
    from app.models.crm import Stage

    async with async_session() as session:
        result = await session.execute(select(Stage).limit(1))
        if result.scalar_one_or_none():
            print("[SKIP] Stages already exist")
            return
        stages = [
            Stage(name="初步接触", probability=10, sort_order=1),
            Stage(name="需求分析", probability=30, sort_order=2),
            Stage(name="方案制定", probability=50, sort_order=3),
            Stage(name="商务谈判", probability=70, sort_order=4),
            Stage(name="合同签订", probability=90, sort_order=5),
            Stage(name="赢单", probability=100, sort_order=6, is_closed_won=True),
            Stage(name="输单", probability=0, sort_order=7, is_closed_lost=True),
        ]
        session.add_all(stages)
        await session.commit()
        print("[OK] Created 7 default stages")


def load_test_data():
    """4. 加载测试数据"""
    print("\n── 加载测试数据 ──")
    run_sql("TEST.sql")


def show_menu() -> str:
    print("=" * 50)
    print("  Husky CRM — 演示数据初始化工具")
    print("=" * 50)
    print()
    print("  1. 创建数据库表结构")
    print("  2. 创建管理员账号 (admin / admin123)")
    print("  3. 创建销售阶段")
    print("  4. 加载测试数据 (TEST.sql)")
    print()
    print("  0. 退出")
    print()
    return input("  请选择操作 (0-4): ").strip()


async def main():
    while True:
        choice = show_menu()

        if choice == "1":
            await init_tables()
        elif choice == "2":
            await seed_admin()
        elif choice == "3":
            await seed_stages()
        elif choice == "4":
            load_test_data()
        elif choice == "0":
            print("\n再见！")
            break
        else:
            print("\n[ERROR] 无效选择，请输入 0-4")

        print("\n" + "-" * 50)
        input("按 Enter 键继续...")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
