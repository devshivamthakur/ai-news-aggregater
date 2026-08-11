from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_admin
from app.api.schemas import (
    CategoryCreate,
    CategoryOut,
    CategoryPatch,
)
from app.services.category_service import CategoryService
from app.storage.cache import cached, invalidate_on_update

router = APIRouter()


@router.get("/categories", response_model=list[CategoryOut], tags=["categories"])
@cached("categories")
def list_categories(
    db: Annotated[Session, Depends(get_db)],
    active_only: bool = Query(True),
) -> list[CategoryOut]:
    """List all categories."""
    return CategoryService(db).list_categories(active_only=active_only)


@router.get("/categories/{category_id}", response_model=CategoryOut, tags=["categories"])
@cached("category_by_id")
def get_category(
    category_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> CategoryOut:
    """Get a category by ID."""
    row = CategoryService(db).get_by_id(category_id)
    if not row:
        raise HTTPException(status_code=404, detail="Category not found")
    return CategoryOut.model_validate(row)


@router.post(
    "/categories",
    response_model=CategoryOut,
    tags=["categories"],
    dependencies=[Depends(require_admin)],
)
@invalidate_on_update("categories", "category_by_id")
def create_category(
    body: CategoryCreate,
    db: Annotated[Session, Depends(get_db)],
) -> CategoryOut:
    """Create a new category (admin only)."""
    try:
        row = CategoryService(db).create(
            name=body.name,
            description=body.description,
            is_active=body.is_active,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return CategoryOut.model_validate(row)


@router.patch(
    "/categories/{category_id}",
    response_model=CategoryOut,
    tags=["categories"],
    dependencies=[Depends(require_admin)],
)
@invalidate_on_update("categories", "category_by_id")
def patch_category(
    category_id: int,
    body: CategoryPatch,
    db: Annotated[Session, Depends(get_db)],
) -> CategoryOut:
    """Update a category (admin only)."""
    try:
        row = CategoryService(db).update(
            category_id,
            name=body.name,
            description=body.description,
            is_active=body.is_active,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    if not row:
        raise HTTPException(status_code=404, detail="Category not found")
    return CategoryOut.model_validate(row)


@router.delete(
    "/categories/{category_id}",
    status_code=204,
    tags=["categories"],
    dependencies=[Depends(require_admin)],
)
@invalidate_on_update("categories", "category_by_id")
def delete_category(
    category_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    """Delete a category (admin only)."""
    success = CategoryService(db).delete(category_id)
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")


@router.post(
    "/categories/sync-defaults",
    tags=["categories"],
    dependencies=[Depends(require_admin)],
)
@invalidate_on_update("categories", "category_by_id")
def sync_default_categories(db: Annotated[Session, Depends(get_db)]) -> dict:
    """Sync default categories from seed data (admin only)."""
    return CategoryService(db).sync_defaults()
