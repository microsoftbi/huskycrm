"""
Seed test data for Husky CRM system.

Creates products, accounts, and contacts via the REST API.
Run this against a running backend server.

Usage:
    python scripts/seed_data.py [--base-url http://localhost:8000/api]
"""

import argparse
import random
import sys
from typing import Any

import requests

API_URL = "http://localhost:8000/api"


# ── Seed data ─────────────────────────────────────────────────────────

PRODUCTS = [
    {"name": "东风导弹", "product_code": "DF-41", "price": 50000000, "category": "导弹"},
    {"name": "小男孩原子弹", "product_code": "MK-1", "price": 2000000000, "category": "核武器"},
    {"name": "大伊万", "product_code": "AN602", "price": 5000000000, "category": "核武器"},
    {"name": "卡秋莎火箭弹", "product_code": "BM-13", "price": 50000, "category": "火箭弹"},
    {"name": "T50坦克", "product_code": "T-50", "price": 30000000, "category": "坦克"},
    {"name": "Z50装甲车", "product_code": "Z-50", "price": 15000000, "category": "装甲车"},
    {"name": "QBZ突击步枪", "product_code": "QBZ-95", "price": 5000, "category": "枪支"},
    {"name": "G0武装直升机", "product_code": "G-0", "price": 80000000, "category": "直升机"},
]

ACCOUNTS = [
    {"name": "俄罗斯", "industry": "军工", "billing_country": "俄罗斯"},
    {"name": "利比亚", "industry": "石油", "billing_country": "利比亚"},
    {"name": "巴基斯坦", "industry": "军工", "billing_country": "巴基斯坦"},
    {"name": "塔吉克斯坦", "industry": "矿业", "billing_country": "塔吉克斯坦"},
    {"name": "红俄罗斯", "industry": "科技", "billing_country": "未知"},
    {"name": "哈哈克斯坦", "industry": "能源", "billing_country": "哈哈克斯坦"},
]

FIRST_NAMES = [
    "亚历山大", "尼古拉", "弗拉基米尔", "德米特里", "米哈伊尔",
    "阿卜杜勒", "穆罕默德", "阿里", "哈桑", "侯赛因",
    "艾哈迈德", "奥马尔", "卡里姆", "拉希德", "贾马尔",
    "伊万", "彼得", "谢尔盖", "安德烈", "马克西姆",
]

LAST_NAMES = [
    "伊万诺夫", "斯米尔诺夫", "库兹涅佐夫", "波波夫", "瓦西里耶夫",
    "彼得罗夫", "索科洛夫", "米哈伊洛夫", "诺维科夫", "费奥多罗夫",
    "阿卜杜拉耶夫", "卡里莫夫", "拉赫莫诺夫", "阿利耶夫", "侯赛因诺夫",
]

TITLES = ["总经理", "采购总监", "军事顾问", "技术总监", "项目经理", "财务总监", "运营主管", "销售经理"]


def _random_name() -> tuple[str, str]:
    return random.choice(FIRST_NAMES), random.choice(LAST_NAMES)


# ── Helpers ───────────────────────────────────────────────────────────

def login(base_url: str) -> str | None:
    """Login as admin and return a bearer token."""
    resp = requests.post(f"{base_url}/auth/login", json={
        "username": "admin",
        "password": "admin123",
    })
    if resp.status_code == 200:
        return resp.json()["access_token"]
    # Maybe not seeded yet — try register
    print("Admin login failed, attempting registration…")
    resp = requests.post(f"{base_url}/auth/register", json={
        "username": "admin",
        "email": "admin@huskycrm.local",
        "password": "admin123",
        "display_name": "Administrator",
    })
    if resp.status_code == 201:
        # Login again
        resp = requests.post(f"{base_url}/auth/login", json={
            "username": "admin",
            "password": "admin123",
        })
        if resp.status_code == 200:
            return resp.json()["access_token"]
    print(f"ERROR: Could not authenticate — {resp.status_code} {resp.text}", file=sys.stderr)
    return None


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _post(base_url: str, token: str, path: str, data: dict) -> dict[str, Any] | None:
    resp = requests.post(f"{base_url}{path}", headers=_headers(token), json=data)
    if resp.status_code in (200, 201):
        return resp.json()
    print(f"  ERROR {resp.status_code}: {resp.text}", file=sys.stderr)
    return None


# ── Main ──────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Seed test data for Husky CRM")
    parser.add_argument("--base-url", default=API_URL, help="API base URL")
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")

    # 1. Authenticate
    token = login(base_url)
    if not token:
        sys.exit(1)

    print(f"Authenticated as admin\n")

    # 2. Create products
    print("── Products ──")
    product_ids: list[int] = []
    for p in PRODUCTS:
        result = _post(base_url, token, "/products", p)
        if result:
            product_ids.append(result["id"])
            print(f"  ✓ {p['name']} ({p['product_code']})")
    print(f"  Total: {len(product_ids)} products created\n")

    # 3. Create accounts
    print("── Accounts ──")
    account_ids: list[int] = []
    for a in ACCOUNTS:
        result = _post(base_url, token, "/accounts", a)
        if result:
            account_ids.append(result["id"])
            print(f"  ✓ {a['name']}")
    print(f"  Total: {len(account_ids)} accounts created\n")

    # 4. Create contacts (2 per account)
    print("── Contacts ──")
    contact_count = 0
    for aid, acc in zip(account_ids, ACCOUNTS):
        for _ in range(2):
            first, last = _random_name()
            title = random.choice(TITLES)
            result = _post(base_url, token, "/contacts", {
                "first_name": first,
                "last_name": last,
                "account_id": aid,
                "title": title,
                "email": f"{first.lower()}.{last.lower()}@example.com",
            })
            if result:
                contact_count += 1
                print(f"  ✓ {first} {last} — {acc['name']} ({title})")
    print(f"  Total: {contact_count} contacts created\n")

    print("✅ Seed data generation complete!")


if __name__ == "__main__":
    main()
