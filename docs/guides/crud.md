# Example of a Simple Flask CRUD App

A simple Flask / SQLite / Jinja app with routes to: **C**reate, **R**ead, **U**pdate, **D**elete data.


## App Configuration

### DB Schema

```SQL
CREATE TABLE bills (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    title   TEXT NOT NULL,
    body    TEXT,
    pinned  INTEGER DEFAULT 0,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### App Routes

| Method | Route                   | Description           |
| ------ | ----------------------- | --------------------- |
| `GET`  | `/`                     | list all bills (home) |
| `GET`  | `/bill/<int:id>`        | show a single bill    |
| `GET`  | `/bill/new`             | new bill form         |
| `POST` | `/bill`                 | add a new bill        |
| `GET`  | `/bill/<int:id>/edit`   | not edit form         |
| `POST` | `/bill/<int:id>`        | update a bill         |
| `GET`  | `/bill/<int:id>/delete` | delete a bill         |


### App Templates

| Name                   | Data Needed | Description                  |
| ---------------------- | ----------- | ---------------------------- |
| `bill_list.jinja`      | `bills[]`   | Show a list of all bills     |
| `bill_single.jinja`    | `bill`      | Show a single bill in detail |
| `bill_form.jinja`      |             | Show a new bill form         |
| `bill_form_edit.jinja` | `bill`      | Show a bill edit form        |


## Routes and Handlers

### Reading bills

```python
# Show all bills -------------------------------------------
@app.get("/")
def show_bills():
    with connect_db() as db:
        sql = """
            SELECT id, title, body, pinned, created
            FROM bills
            ORDER BY pinned DESC, created DESC
        """
        params = ()
        bills = db.execute(sql, params).fetchall()

        return render_template("pages/bill_list.jinja", bills=bills)


# Show a single bill ----------------------------------------
@app.get("/bill/<int:id>")
def show_a_bill(id):
    with connect_db() as db:
        sql = """
            SELECT id, title, body, pinned, created
            FROM bills
            WHERE id=?
        """
        params = (id,)
        bill = db.execute(sql, params).fetchone()

        return render_template("pages/bill_single.jinja", bill=bill)
```

### Creating bills

```python
# Show new bill form ----------------------------------------
@app.get("/bill/new")
def show_bill_form():
    return render_template("pages/bill_form.jinja")


# Process new bill ------------------------------------------
@app.post("/bill")
def add_a_bill():
    title = request.form.get('title', '').strip()
    body = request.form.get('body', '').strip()

    pinned = bool(request.form.get('pin'))

    title = html.escape(title)
    body = html.escape(body)

    with connect_db() as db:
        sql = """
            INSERT INTO bills (title, body, pinned)
            VALUES (?, ?, ?)
        """
        params = (title, body, pinned)
        db.execute(sql, params)

        flash("bill added", "success")
        return redirect("/")
```

### Updating bills

```python
# Show bill edit form with existing data --------------------
@app.get("/bill/<int:id>/edit")
def show_bill_edit_form(id):
    with connect_db() as db:
        sql = """
            SELECT id, title, body, pinned, created
            FROM bills
            WHERE id=?
        """
        params = (id,)
        bill = db.execute(sql, params).fetchone()

        return render_template("pages/bill_form_edit.jinja", bill=bill)


# Process updated bill --------------------------------------
@app.post("/bill/<int:id>")
def update_a_bill(id):
    title = request.form.get('title', '').strip()
    body = request.form.get('body', '').strip()

    pinned = bool(request.form.get('pin'))

    title = html.escape(title)
    body = html.escape(body)

    with connect_db() as db:
        sql = """
            UPDATE bills
            SET title=?, body=?, pinned=?
            WHERE id=?
        """
        params = (title, body, pinned, id)
        db.execute(sql, params)

        flash("bill updated", "success")
        return redirect("/")
```

### Deleting bills

```python
# Delete a bill ---------------------------------------------
@app.get("/bill/<int:id>/delete")
def delete_a_bill(id):
    with connect_db() as db:
        sql = """
            DELETE FROM bills
            WHERE id=?
        """
        params = (id,)
        db.execute(sql, params)

        flash("bill deleted", "success")
        return redirect("/")
```


## Jinja Templates

### bills_list.jinja

```jinja
{% raw %}{% block content %}

    <section class="bills">
        {% for bill in bills %}

            <article class="bill {{ 'pinned' if bill.pinned }}">

                <header>
                    <h3>{{ bill.title }}</h3>
                    {{ "📌" if bill.pinned }}
                </header>

                <p><a href="/bill/{{ bill.id }}">View bill...</a></p>

            </article>

        {% else %}

            <p>No bills!</p>

        {% endfor %}
    </section>

{% endblock %}  {% endraw %}
```

### bill_single.jinja

```jinja
{% raw %}{% block content %}

<article class="bill {{ 'pinned' if bill.pinned }}">

    <header>
        <h3>{{ bill.title }}</h3>
        {{ "📌" if bill.pinned }}
    </header>

    <p>{{ bill.body | paragraphs }}</p>

    <footer>
        <span>Created on {{ bill.created | local | format }}</span>

        <span><a href="/bill/{{ bill.id }}/edit">🖊️ Edit</a></span>
        <span><a href="/bill/{{ bill.id }}/delete"
                 onclick="return confirm('Really delete?')">🗑 Delete</a></span>
    </footer>

</article>

{% endblock %}  {% endraw %}
```

### bill_form.jinja

```jinja
{% raw %}{% block content %}

<article>

    <form method="post" action="/bill">
        <h3>New bill</h3>

        <label>
            Title
            <input name="title" type="text" required>
        </label>

        <label>
            Body
            <textarea name="body" required></textarea>
        </label>

        <label>
            <input name="pin" type="checkbox">
            Pin bill?
        </label>

        <button>Add bill</button>
    </form>

</article>

{% endblock %}  {% endraw %}
```

### bill_form_edit.jinja

```jinja
{% raw %}{% block content %}

<article>

    <form method="post" action="/bill/{{ bill.id }}">
        <h3>Edit bill</h3>

        <label>
            Title
            <input name="title" type="text" value="{{ bill.title }}" required>
        </label>

        <label>
            Body
            <textarea name="body" required>{{ bill.body }}</textarea>
        </label>

        <label>
            <input name="pin" type="checkbox" {{ 'checked' if bill.pinned }}>
            Pin bill?
        </label>

        <button>Update bill</button>
    </form>

</article>

{% endblock %}  {% endraw %}
```
