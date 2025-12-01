"""Flask application for warehouse management."""
import os
from flask import Flask, render_template, request, redirect, url_for
from varasto import Varasto


app = Flask(__name__)

# In-memory storage for warehouses
warehouses = {}
_id_counter = [1]


def get_next_id():
    """Get the next available warehouse ID."""
    current_id = _id_counter[0]
    _id_counter[0] += 1
    return current_id


@app.route('/')
def index():
    """Display list of all warehouses."""
    return render_template('index.html', warehouses=warehouses)


def _parse_create_form():
    """Parse and validate the create warehouse form."""
    name = request.form.get('name', '').strip()
    tilavuus = float(request.form.get('tilavuus', 0))
    alku_saldo = float(request.form.get('alku_saldo', 0))
    return name, tilavuus, alku_saldo


@app.route('/warehouse/create', methods=['GET', 'POST'])
def create_warehouse():
    """Create a new warehouse."""
    if request.method == 'POST':
        try:
            name, tilavuus, alku_saldo = _parse_create_form()
        except (ValueError, TypeError):
            error = 'Invalid capacity or initial balance'
            return render_template('create.html', error=error)

        if not name:
            return render_template('create.html', error='Name is required')

        warehouse_id = get_next_id()
        warehouses[warehouse_id] = {
            'id': warehouse_id,
            'name': name,
            'varasto': Varasto(tilavuus, alku_saldo)
        }
        return redirect(url_for('index'))

    return render_template('create.html')


@app.route('/warehouse/<int:warehouse_id>')
def view_warehouse(warehouse_id):
    """View a specific warehouse."""
    warehouse = warehouses.get(warehouse_id)
    if not warehouse:
        return redirect(url_for('index'))
    return render_template('view.html', warehouse=warehouse)


def _handle_edit_post(warehouse, warehouse_id):
    """Handle POST request for editing warehouse."""
    name = request.form.get('name', '').strip()
    try:
        tilavuus = float(request.form.get('tilavuus', 0))
    except (ValueError, TypeError):
        return render_template(
            'edit.html', warehouse=warehouse, error='Invalid capacity'
        )

    if not name:
        return render_template(
            'edit.html', warehouse=warehouse, error='Name is required'
        )

    warehouse['name'] = name
    old_saldo = warehouse['varasto'].saldo
    warehouse['varasto'] = Varasto(tilavuus, old_saldo)
    return redirect(url_for('view_warehouse', warehouse_id=warehouse_id))


@app.route('/warehouse/<int:warehouse_id>/edit', methods=['GET', 'POST'])
def edit_warehouse(warehouse_id):
    """Edit warehouse details."""
    warehouse = warehouses.get(warehouse_id)
    if not warehouse:
        return redirect(url_for('index'))

    if request.method == 'POST':
        return _handle_edit_post(warehouse, warehouse_id)

    return render_template('edit.html', warehouse=warehouse)


@app.route('/warehouse/<int:warehouse_id>/delete', methods=['POST'])
def delete_warehouse(warehouse_id):
    """Delete a warehouse."""
    if warehouse_id in warehouses:
        del warehouses[warehouse_id]
    return redirect(url_for('index'))


@app.route('/warehouse/<int:warehouse_id>/add', methods=['POST'])
def add_content(warehouse_id):
    """Add content to a warehouse."""
    warehouse = warehouses.get(warehouse_id)
    if not warehouse:
        return redirect(url_for('index'))

    try:
        amount = float(request.form.get('amount', 0))
    except (ValueError, TypeError):
        return redirect(url_for('view_warehouse', warehouse_id=warehouse_id))

    warehouse['varasto'].lisaa_varastoon(amount)
    return redirect(url_for('view_warehouse', warehouse_id=warehouse_id))


@app.route('/warehouse/<int:warehouse_id>/remove', methods=['POST'])
def remove_content(warehouse_id):
    """Remove content from a warehouse."""
    warehouse = warehouses.get(warehouse_id)
    if not warehouse:
        return redirect(url_for('index'))

    try:
        amount = float(request.form.get('amount', 0))
    except (ValueError, TypeError):
        return redirect(url_for('view_warehouse', warehouse_id=warehouse_id))

    warehouse['varasto'].ota_varastosta(amount)
    return redirect(url_for('view_warehouse', warehouse_id=warehouse_id))


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
