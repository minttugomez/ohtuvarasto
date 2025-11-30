""" Flask web application for warehouse management """

from flask import Flask, render_template, request, redirect, url_for, jsonify
from varasto import Varasto

app = Flask(__name__)

# In-memory storage for warehouses
warehouses = {}
WAREHOUSE_COUNTER = [0]  # Using a list to avoid global statement


def get_next_id():
    """ Generate next warehouse ID """
    WAREHOUSE_COUNTER[0] += 1
    return WAREHOUSE_COUNTER[0]


@app.route('/')
def index():
    """ Main page showing all warehouses """
    warehouse_list = [
        {
            'id': wid,
            'tilavuus': w.tilavuus,
            'saldo': w.saldo,
            'tilaa': w.paljonko_mahtuu()
        }
        for wid, w in warehouses.items()
    ]
    return render_template('index.html', warehouses=warehouse_list)


@app.route('/warehouse/create', methods=['POST'])
def create_warehouse():
    """ Create a new warehouse """
    tilavuus = float(request.form.get('tilavuus', 10))
    alku_saldo = float(request.form.get('alku_saldo', 0))
    wid = get_next_id()
    warehouses[wid] = Varasto(tilavuus, alku_saldo)
    return redirect(url_for('index'))


@app.route('/warehouse/<int:wid>/edit', methods=['POST'])
def edit_warehouse(wid):
    """ Edit warehouse capacity """
    if wid not in warehouses:
        return redirect(url_for('index'))

    new_tilavuus = float(request.form.get('tilavuus', 10))
    current = warehouses[wid]
    # Create new warehouse with same balance, new capacity
    warehouses[wid] = Varasto(new_tilavuus, current.saldo)
    return redirect(url_for('index'))


@app.route('/warehouse/<int:wid>/delete', methods=['POST'])
def delete_warehouse(wid):
    """ Delete a warehouse """
    if wid in warehouses:
        del warehouses[wid]
    return redirect(url_for('index'))


@app.route('/warehouse/<int:wid>/add', methods=['POST'])
def add_to_warehouse(wid):
    """ Add items to warehouse """
    if wid not in warehouses:
        return redirect(url_for('index'))

    maara = float(request.form.get('maara', 0))
    warehouses[wid].lisaa_varastoon(maara)
    return redirect(url_for('index'))


@app.route('/warehouse/<int:wid>/remove', methods=['POST'])
def remove_from_warehouse(wid):
    """ Remove items from warehouse """
    if wid not in warehouses:
        return redirect(url_for('index'))

    maara = float(request.form.get('maara', 0))
    warehouses[wid].ota_varastosta(maara)
    return redirect(url_for('index'))


@app.route('/api/warehouse/<int:wid>')
def get_warehouse_details(wid):
    """ API endpoint to get warehouse details """
    if wid not in warehouses:
        return jsonify({'error': 'Warehouse not found'}), 404

    w = warehouses[wid]
    return jsonify({
        'id': wid,
        'tilavuus': w.tilavuus,
        'saldo': w.saldo,
        'tilaa': w.paljonko_mahtuu()
    })


if __name__ == '__main__':
    app.run(debug=True)
