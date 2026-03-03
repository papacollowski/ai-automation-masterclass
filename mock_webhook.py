from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
import json
import random
import string


class ZapierPayload(BaseModel):
    name: str
    email: EmailStr
    signup_date: datetime


def generate_fake_payload() -> ZapierPayload:
    """Generate a fake customer signup payload and validate it."""
    fake_name = "".join(random.choices(string.ascii_letters, k=8)).title()
    fake_email = f"{''.join(random.choices(string.ascii_lowercase, k=6))}@example.com"
    fake_date = datetime.now() - timedelta(days=random.randint(0, 365))

    payload = ZapierPayload(name=fake_name, email=fake_email, signup_date=fake_date)
    return payload


if __name__ == "__main__":
    payload = generate_fake_payload()
    print(json.dumps(payload.model_dump(mode="json"), indent=2))
