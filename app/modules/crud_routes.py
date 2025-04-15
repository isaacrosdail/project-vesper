## Generalized CRUD handling routes for ANY module/model :P
## STRONGLY consider moving to a future utils or helpers directory in future

from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from app.core.database import db_session

### Steps to Generalize ADD
