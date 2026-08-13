from flask import Flask, render_template, request, url_for, redirect
from conexao import conection

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('base.html')


@app.route('/clientes', methods=['GET', 'POST'])
def clientes():
    conn = conection()
    cursor = conn.cursor()

    if request.method == 'POST':
        cliente = request.form.get('nome')

        if cliente:
            cursor.execute(
                'INSERT INTO clientes (nome) VALUES (?)',
                (cliente.capitalize(),)
            )
            conn.commit()

        conn.close()
        return redirect(url_for('clientes'))

    clientes_cadastrados = cursor.execute('SELECT * FROM clientes').fetchall()
    contagem_clientes = cursor.execute(
        'SELECT count(*) FROM clientes').fetchone()

    conn.close()

    return render_template(
        'clientes.html',
        clientes_cadastrados=clientes_cadastrados, contagem_clientes=contagem_clientes
    )


@app.route('/clientes/<int:id>/editar', methods=['GET', 'POST'])
def editar_cliente(id):
    conn = conection()
    cursor = conn.cursor()

    if request.method == 'POST':
        cliente = request.form.get('nome')

        if cliente:
            cursor.execute('UPDATE clientes set nome = ? WHERE id = ?',
                           (cliente.capitalize().strip(), id))
            conn.commit()
            conn.close()
            return redirect(url_for('clientes'))

    dados = cursor.execute(
        'SELECT * FROM clientes WHERE ID = ?', (id,)).fetchone()

    conn.close()

    return render_template('editar_cliente.html', dados=dados[1])


@app.route('/produtos', methods=['GET', 'POST'])
def produtos():
    conn = conection()
    cursor = conn.cursor()

    if request.method == 'POST':
        produto = request.form.get('nome')
        preco = request.form.get('preco')

        validation = cursor.execute(
            'SELECT nome FROM produtos WHERE nome = ?',
            (produto,)
        ).fetchone()

        if validation:
            msg = 'Produto já existente'
            conn.close()
            return render_template('produtos.html', msg=msg)

        cursor.execute(
            'INSERT INTO produtos (nome, preco) VALUES (?, ?)',
            (produto.strip().title(), float(preco))
        )

        conn.commit()
        conn.close()

        return redirect(url_for('produtos'))

    dados = cursor.execute(
        'SELECT * FROM produtos'
    ).fetchall()

    contagem_dados = cursor.execute('SELECT COUNT(*) FROM produtos').fetchone()

    conn.close()

    return render_template(
        'produtos.html',
        dados=dados, contagem_dados=contagem_dados[0]
    )


@app.route('/produtos/<int:id>/editar', methods=['GET', 'POST'])
def editar_produto(id):
    conn = conection()
    cursor = conn.cursor()

    if request.method == 'POST':

        nome = request.form.get('nome')
        preco = request.form.get('preco')

        if all([nome, preco]):
            cursor.execute('UPDATE produtos set nome = ?, preco = ? WHERE id = ?',
                           (nome.strip().title(), float(preco), id))

            conn.commit()
            conn.close()
            return redirect(url_for('produtos'))

    dados = cursor.execute('SELECT * FROM produtos WHERE id = ?',
                           (id,)).fetchone()
    conn.close()

    return render_template('editar_produto.html', dados=dados)


@app.route('/caixa', methods=['GET', 'POST'])
def caixa():

    conn = conection()
    cursor = conn.cursor()

    dados = None
    total = None
    cliente_nome = None

    if request.method == 'POST':
        acao = request.form.get('acao')
        if acao == 'resumo':
            cliente_id = request.form.get('cliente_id')
            if cliente_id:
                dados = cursor.execute(
                    '''
                SELECT p.nome, p.preco, v.quantidade, v.total
                FROM produtos AS p
                JOIN vendas AS v
                ON p.id = v.produto_id
                WHERE v.cliente_id = ? AND v.status = "pendente"
                    ''',
                    (cliente_id,)).fetchall()

                total = cursor.execute(
                    '''
                SELECT SUM(total) FROM vendas WHERE cliente_id = ? AND status = "pendente"
                    ''',
                    (cliente_id,)).fetchone()

                cliente_nome = cursor.execute('SELECT nome FROM clientes WHERE id = ?',
                                              (cliente_id,)).fetchone()

        elif acao == 'adicionar':
            cliente_id = request.form.get('cliente_id')
            produto_id = request.form.get('produto_id')
            quantidade = int(request.form.get('quantidade'))
            if all([cliente_id, produto_id, quantidade]):
                valor = cursor.execute('SELECT preco FROM produtos WHERE id = ?',
                                       (produto_id,)).fetchone()
                if valor:
                    total_parcial = (valor[0] * quantidade)

                    cursor.execute('INSERT INTO vendas (cliente_id,produto_id,quantidade, total) VALUES (?,?,?,?)',
                                   (cliente_id, produto_id, quantidade, total_parcial))
                    conn.commit()
                    conn.close()
                    return redirect(url_for('caixa'))

    clientes = cursor.execute('SELECT * FROM clientes').fetchall()
    produtos = cursor.execute('SELECT * FROM produtos').fetchall()

    conn.close()
    return render_template('caixa.html', clientes=clientes, produtos=produtos, dados=dados, total=total, cliente_nome=cliente_nome)


if __name__ == '__main__':
    app.run(debug=True)
