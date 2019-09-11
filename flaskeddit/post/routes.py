from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from flaskeddit.community import community_service
from flaskeddit.post import post_blueprint, post_service
from flaskeddit.post.forms import PostForm, UpdatePostForm


@post_blueprint.route("/community/<string:name>/post/<string:title>")
def post(name, title):
    """Route for viewing a post and its replies sorted by date created."""
    page = int(request.args.get("page", 1))
    post = post_service.get_post_with_votes(title, name)
    if post:
        replies = post_service.get_replies(post.id, page, False)
        return render_template("post.jinja2", page="recent", post=post, replies=replies)
    else:
        abort(404)


@post_blueprint.route("/community/<string:name>/post/<string:title>/top")
def top_post(name, title):
    """Route for viewing a post and its replies sorted by upvotes."""
    page = int(request.args.get("page", 1))
    post = post_service.get_post_with_votes(title, name)
    if post:
        replies = post_service.get_replies(post.id, page, True)
        return render_template("post.jinja2", page="top", post=post, replies=replies)
    else:
        abort(404)


@post_blueprint.route("/community/<string:name>/post/create", methods=["GET", "POST"])
@login_required
def create_post(name):
    """Route for creating a post."""
    community = community_service.get_community(name)
    if community:
        form = PostForm()
        form.community_id.data = community.id
        if form.validate_on_submit():
            post_service.create_post(
                form.title.data, form.post.data, community, current_user
            )
            flash("Successfully created post.", "primary")
            return redirect(url_for("post.post", name=name, title=form.title.data))
        return render_template("create_post.jinja2", name=name, form=form)
    else:
        abort(404)


@post_blueprint.route(
    "/community/<string:name>/post/<string:title>/update", methods=["GET", "POST"]
)
@login_required
def update_post(name, title):
    """Route for updating a post."""
    post = post_service.get_post(title, name)
    if post:
        if post.user_id != current_user.id:
            return redirect(url_for("post.post", name=name, title=title))
        form = UpdatePostForm()
        if form.validate_on_submit():
            post_service.update_post(post, form.post.data)
            flash("Successfully updated post.", "primary")
            return redirect(url_for("post.post", name=name, title=title))
        form.post.data = post.post
        return render_template("update_post.jinja2", name=name, title=title, form=form)
    else:
        abort(404)


@post_blueprint.route(
    "/community/<string:name>/post/<string:title>/delete", methods=["POST"]
)
@login_required
def delete_post(name, title):
    """Route for deleting a post."""
    post = post_service.get_post(title, name)
    if post:
        if post.user_id != current_user.id:
            return redirect(url_for("post.post", name=name, title=title))
        post_service.delete_post(post)
        flash("Successfully deleted post.", "primary")
        return redirect(url_for("community.community", name=name))
    else:
        abort(404)


@post_blueprint.route(
    "/community/<string:name>/post/<string:title>/upvote", methods=["POST"]
)
@login_required
def upvote_post(name, title):
    """Route for upvoting a post."""
    post = post_service.get_post(title, name)
    if post:
        post_service.upvote_post(post.id, current_user.id)
        return redirect(request.referrer)
    else:
        abort(404)


@post_blueprint.route(
    "/community/<string:name>/post/<string:title>/downvote", methods=["POST"]
)
@login_required
def downvote_post(name, title):
    """Route for downvoting a post."""
    post = post_service.get_post(title, name)
    if post:
        post_service.downvote_post(post.id, current_user.id)
        return redirect(request.referrer)
    else:
        abort(404)
