from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.setting import Setting
from app.schemas.setting import SettingsResponse, SettingsUpdate
from app.config import get_settings as get_env_settings

router = APIRouter(prefix="/settings", tags=["settings"])


async def _get_all(db: AsyncSession) -> dict[str, str]:
    result = await db.execute(select(Setting))
    return {r.key: r.value for r in result.scalars().all()}


@router.get("", response_model=SettingsResponse)
async def get_settings(db: AsyncSession = Depends(get_db)):
    db_settings = await _get_all(db)
    env = get_env_settings()

    return SettingsResponse(
        api_key=db_settings.get("api_key", env.deepseek_api_key),
        base_url=db_settings.get("base_url", env.deepseek_base_url),
        chat_model=db_settings.get("chat_model", env.deepseek_chat_model),
        temperature=float(
            db_settings.get("temperature", env.chat_temperature)
        ),
        max_tokens=int(db_settings.get("max_tokens", env.chat_max_tokens)),
        top_k=int(
            db_settings.get("top_k", env.search_default_top_k)
        ),
        system_prompt=db_settings.get("system_prompt", ""),
    )


@router.put("", response_model=SettingsResponse)
async def update_settings(
    update: SettingsUpdate,
    db: AsyncSession = Depends(get_db),
):
    updates = update.model_dump(exclude_none=True)

    for key, value in updates.items():
        result = await db.execute(
            select(Setting).where(Setting.key == key)
        )
        setting = result.scalar_one_or_none()
        if setting:
            setting.value = str(value)
        else:
            db.add(Setting(key=key, value=str(value)))

    await db.commit()

    return await get_settings(db)
