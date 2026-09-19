from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime

from routes.auth import user_dependency, db_dependency
from schema.userSchema import ComplaintCreate,ComplaintUpdate
from models import Users, Complaints


router = APIRouter()


# -> add complaint
@router.post("/complaints")
def create_complaint(
    db: db_dependency,
    user: user_dependency,
    complaint: ComplaintCreate
):
    if user is None:
        raise HTTPException(
            status_code=401,
            detail={
                "message": "User not found"
            }
        )
        
    new_complaint = Complaints(
        title=complaint.title,
        description=complaint.description,
        category=complaint.category,
        location=complaint.location,
        status="Pending",
        user_id=user.get("id")
    )
    
    db.add(new_complaint)
    db.commit()
    db.refresh(new_complaint)
    
    
    
    return JSONResponse(status_code=200,content={
        "message": "Complaint created successfully",
        "complaint_id": new_complaint.id
    })
    

# -> read all my complaints
@router.get("/complaints/my")
def get_my_complaints(
    user: user_dependency,
    db: db_dependency
):
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not authenticated"
        )

    complaints = db.query(Complaints).filter(
        Complaints.user_id == user.get("id")
    ).order_by(
        Complaints.created_at.desc()
    ).all()

    if not complaints:
        raise HTTPException(
            status_code=404,
            detail="No complaints found"
        )

    return complaints


# -> read specific complaint
@router.get("/complaints/{id}")
def get_specific_complaint(
    id: int,
    user: user_dependency,
    db: db_dependency
):
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not authenticated"
        )

    complaint = db.query(Complaints).filter(
        Complaints.id == id
    ).first()

    if complaint is None:
        raise HTTPException(
            status_code=404,
            detail="Complaint not found"
        )

    
    if user.get("role") == "admin":
        return complaint

    
    if complaint.user_id != user.get("id"):
        raise HTTPException(
            status_code=403,
            detail="You can only view your own complaint"
        )

    return complaint


# -> update complaint 
@router.put("/complaints/{complaint_id}")
def update_complaint(
    complaint_id: int,
    complaint_data: ComplaintUpdate,
    user: user_dependency,
    db: db_dependency
):
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not authenticated"
        )

    complaint = db.query(Complaints).filter(
        Complaints.id == complaint_id
    ).first()

    if not complaint:
        raise HTTPException(
            status_code=404,
            detail="Complaint not found"
        )

    if complaint.user_id != user.get("id"):
        raise HTTPException(
            status_code=403,
            detail="You can only update your own complaint"
        )

    update_data = complaint_data.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(complaint, key, value)

    complaint.updated_at = datetime.now()

    db.commit()

    return {
        "message": "Complaint updated successfully"
    }
    
# -> delete complaint
@router.delete("/complaints/{complaint_id}")
def delete_complaint(
    complaint_id: int,
    user: user_dependency,
    db: db_dependency
):
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not authenticated"
        ) 
         
    complaint = db.query(Complaints).filter(
        Complaints.id == complaint_id
    ).first()

    if not complaint:
        raise HTTPException(
            status_code=404,
            detail="Complaint not found"
        )

    if complaint.user_id != user.get("id"):
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own complaint"
        )

    db.delete(complaint)
    db.commit()

    return {
        "message": "Complaint deleted successfully"
    }