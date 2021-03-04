#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import hashlib
import random
import argparse

from CTFd import create_app

from CTFd.cache import clear_config, clear_pages
from CTFd.models import (
    Rights,
    Roles,
    RoleRights,
    UserRights,
    db
)

app = create_app()
with app.app_context():
    db = app.db

    role=Roles()
    role.id=1
    role.name="admin"
    db.session.add(role)
    db.session.commit()

    right=Rights()
    right.id=1
    right.name="admin_panel_statistics"
   
    db.session.add(right)
    db.session.commit()

    role_right=RoleRights()
    role_right.role_id=1
    role_right.right_id=1
    
    db.session.add(role_right)
    db.session.commit()

    user_right=UserRights()
    user_right.user_id=1
    user_right.right_id=1
   
    db.session.add(user_right)
    db.session.commit()


