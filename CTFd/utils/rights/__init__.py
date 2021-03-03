from CTFd.models import Rights, UserRights
from flask import session

def has_right(right_name,author_id):
    right=Rights.query.filter_by(name=right_name).first()
    user_rights=UserRights.query.filter_by(right_id=right.id,user_id=session["id"]).first()
    if right!= None or session["id"]==author_id :
        return True
    else 
        return False
