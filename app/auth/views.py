from flask import Blueprint, render_template

auth_views_bp = Blueprint(
    "auth_views",
    __name__,
)


@auth_views_bp.get("/login")
def login_page():
    return render_template("auth/login.html")


@auth_views_bp.get("/cadastro")
def register_page():
    return render_template("auth/cadastro.html")
