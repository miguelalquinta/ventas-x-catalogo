document.addEventListener('DOMContentLoaded', function () {

    function formatear(valor) {
        return "$" + Number(valor).toLocaleString();
    }

    // ========================
    // FILTRADO POR CAMPAÑA
    // Cada <option> tiene data-campana-id gracias al widget del servidor.
    // Ocultamos/mostramos opciones según la campaña seleccionada.
    // ========================
    const campanaSelect = document.querySelector('select[name="campana"]');

    function filtrarProductosPorCampana(campanaId) {
        const selects = document.querySelectorAll('select[name$="producto_campana"]');

        selects.forEach(function(sel) {
            const valorActual = sel.value;

            Array.from(sel.options).forEach(function(option) {
                if (!option.value) {
                    // Opción vacía: siempre visible
                    option.style.display = '';
                    option.disabled = false;
                    return;
                }

                const optCampanaId = option.getAttribute('data-campana-id');

                if (!campanaId) {
                    // Sin campaña: mostrar todo
                    option.style.display = '';
                    option.disabled = false;
                } else {
                    // Mostrar solo los de la campaña seleccionada
                    const visible = (optCampanaId === String(campanaId));
                    option.style.display = visible ? '' : 'none';
                    option.disabled = !visible;
                }
            });

            // Si el producto seleccionado ya no corresponde a la campaña, resetear
            if (campanaId && sel.value) {
                const selectedOption = sel.options[sel.selectedIndex];
                if (selectedOption) {
                    const optCampanaId = selectedOption.getAttribute('data-campana-id');
                    if (optCampanaId !== String(campanaId)) {
                        sel.value = '';
                        sel.dispatchEvent(new Event('change'));
                    }
                }
            }
        });
    }

    if (campanaSelect) {
        // Filtrar al cambiar campaña
        campanaSelect.addEventListener('change', function () {
            filtrarProductosPorCampana(this.value);
        });

        // Filtrar al cargar si ya hay una campaña seleccionada
        if (campanaSelect.value) {
            filtrarProductosPorCampana(campanaSelect.value);
        }
    }

    // ========================
    // INLINE CATÁLOGO — precio/costo/subtotal
    // ========================
    function initCatalogo(row) {
        const productoSelect = row.querySelector('select[name$="producto_campana"]');
        const cantidadInput = row.querySelector('input[name$="cantidad"]');

        const precioSpan = row.querySelector('.campo-precio');
        const costoSpan = row.querySelector('.campo-costo');
        const subtotalSpan = row.querySelector('.campo-subtotal');
        const gananciaSpan = row.querySelector('.campo-ganancia');

        let precio = 0;
        let costo = 0;

        if (!productoSelect) return;

        function calcular() {
            const cantidad = parseInt(cantidadInput?.value || 0);
            const subtotal = precio * cantidad;
            const ganancia = (precio - costo) * cantidad;
            if (subtotalSpan) subtotalSpan.innerText = formatear(subtotal);
            if (gananciaSpan) gananciaSpan.innerText = formatear(ganancia);
        }

        productoSelect.addEventListener('change', function () {
            const id = this.value;

            if (!id) {
                precio = 0; costo = 0;
                if (precioSpan) precioSpan.innerText = formatear(0);
                if (costoSpan) costoSpan.innerText = formatear(0);
                calcular();
                return;
            }

            fetch(`/productos/api/producto-campana/${id}/`)
                .then(r => r.json())
                .then(data => {
                    precio = data.precio;
                    costo = data.costo;
                    if (precioSpan) precioSpan.innerText = formatear(precio);
                    if (costoSpan) costoSpan.innerText = formatear(costo);
                    calcular();
                });
        });

        if (cantidadInput) {
            cantidadInput.addEventListener('input', calcular);
        }
    }

    // ========================
    // INLINE STOCK — precio/costo/subtotal
    // ========================
    function initStock(row) {
        const productoSelect = row.querySelector('select[name$="producto_stock"]');
        const cantidadInput = row.querySelector('input[name$="cantidad"]');

        const costoSpan = row.querySelector('.campo-costo');
        const subtotalSpan = row.querySelector('.campo-subtotal');
        const gananciaSpan = row.querySelector('.campo-ganancia');

        let precio = 0;
        let costo = 0;

        if (!productoSelect) return;

        function calcular() {
            const cantidad = parseInt(cantidadInput?.value || 0);
            const subtotal = precio * cantidad;
            const ganancia = (precio - costo) * cantidad;
            if (subtotalSpan) subtotalSpan.innerText = formatear(subtotal);
            if (gananciaSpan) gananciaSpan.innerText = formatear(ganancia);
        }

        productoSelect.addEventListener('change', function () {
            const id = this.value;
            if (!id) return;

            fetch(`/stock/api/producto/${id}/`)
                .then(r => r.json())
                .then(data => {
                    precio = data.precio_sugerido;
                    costo = data.costo;
                    if (costoSpan) costoSpan.innerText = formatear(costo);
                    calcular();
                });
        });

        if (cantidadInput) {
            cantidadInput.addEventListener('input', calcular);
        }
    }

    function init() {
        document.querySelectorAll('tr.form-row').forEach(row => {
            initCatalogo(row);
            initStock(row);
        });
    }

    init();

    // Al agregar nueva fila inline
    document.body.addEventListener('click', function (e) {
        if (e.target.closest('.add-row')) {
            setTimeout(function () {
                init();
                // Aplicar filtro de campaña a la nueva fila
                if (campanaSelect && campanaSelect.value) {
                    filtrarProductosPorCampana(campanaSelect.value);
                }
            }, 300);
        }
    });

});
