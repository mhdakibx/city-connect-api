from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
from datetime import datetime

from routes.auth import user_dependency, db_dependency
from schema.userSchema import ComplaintCreate,ComplaintUpdate
from schema.adminSchema import StatusUpdate
from models import Users, Complaints

router = APIRouter()


# -> admin all complaints
@router.get("/admin/complaints")
def get_all_complaints(
    user: user_dependency,
    db: db_dependency,

    search: Optional[str] = None,
    status: Optional[str] = None,
    category: Optional[str] = None,

    sort: str = "newest",

    page: int = 1,
    limit: int = 10
):
    
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not authenticated"
        )

    
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    
    query = db.query(Complaints)

    

    if search:
        query = query.filter(
            Complaints.title.ilike(f"%{search}%")
        )
        

    if status:
        query = query.filter(
            Complaints.status == status
        )


    if category:
        query = query.filter(
            Complaints.category == category
        )


    if sort == "oldest":

        query = query.order_by(
            Complaints.created_at.asc()
        )

    elif sort == "title":

        query = query.order_by(
            Complaints.title.asc()
        )

    else:

        query = query.order_by(
            Complaints.created_at.desc()
        )


    if page < 1:
        page = 1

    if limit < 1:
        limit = 10


    total = query.count()

    
    total_pages = (total + limit - 1) // limit

    
    skip = (page - 1) * limit

    
    complaints = query.offset(skip).limit(limit).all()

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "complaints": complaints
    }
    

# -> admin status update 
@router.put("/admin/complaints/{complaint_id}/status")
def update_complaint_status(
    complaint_id: int,
    status_data: StatusUpdate,
    user: user_dependency,
    db: db_dependency
):

    if user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    allowed_status = [
        "Pending",
        "In Progress",
        "Resolved",
        "Rejected"
    ]

    if status_data.status not in allowed_status:
        raise HTTPException(
            status_code=400,
            detail="Invalid status"
        )

    complaint = db.query(Complaints).filter(
        Complaints.id == complaint_id
    ).first()

    if not complaint:
        raise HTTPException(
            status_code=404,
            detail="Complaint not found"
        )

    complaint.status = status_data.status
    complaint.updated_at = datetime.now()

    db.commit()

    return {
        "message": "Complaint status updated successfully"
    }


# -> admin delete complaint
@router.delete("/admin/complaints/{complaint_id}")
def admin_delete_complaint(
    complaint_id: int,
    user: user_dependency,
    db: db_dependency
):

    if user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    complaint = db.query(Complaints).filter(
        Complaints.id == complaint_id
    ).first()

    if not complaint:
        raise HTTPException(
            status_code=404,
            detail="Complaint not found"
        )

    db.delete(complaint)
    db.commit()

    return {
        "message": "Complaint deleted successfully"
    }